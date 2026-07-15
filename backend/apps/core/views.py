from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth, TruncDay
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.accounts.permissions import IsPlatformAdmin
from apps.accounts.serializers import UserSerializer
from apps.nannies.models import NannyDocument, NannyProfile
from apps.parents.models import ParentProfile
from apps.payments.models import Payment, Subscription
from apps.reviews.models import Review


class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"status": "ok", "service": "pomich-poruch"})


class AdminDashboardView(APIView):
    permission_classes = [IsPlatformAdmin]

    def get(self, request):
        paid_qs = Payment.objects.filter(status=Payment.Status.PAID)
        pending_profiles = NannyProfile.objects.filter(
            moderation_status=NannyProfile.ModerationStatus.PENDING
        ).count()
        pending_docs = NannyDocument.objects.filter(status=NannyDocument.DocStatus.PENDING).count()
        return Response(
            {
                "users_total": User.objects.count(),
                "parents_total": ParentProfile.objects.count(),
                "nannies_total": NannyProfile.objects.count(),
                "payments_count": paid_qs.count(),
                "revenue_uah": paid_qs.aggregate(total=Sum("amount_uah"))["total"] or 0,
                "pending_profiles": pending_profiles,
                "pending_documents": pending_docs,
                "pending_users": User.objects.filter(status=User.Status.PENDING).count(),
                "reviews_total": Review.objects.count(),
            }
        )


class AdminUserListView(APIView):
    permission_classes = [IsPlatformAdmin]

    def get(self, request):
        role = request.query_params.get("role")
        status = request.query_params.get("status")
        qs = User.objects.all().order_by("-date_joined")
        if role in User.Role.values:
            qs = qs.filter(role=role)
        if status in User.Status.values:
            qs = qs.filter(status=status)
        return Response(UserSerializer(qs[:100], many=True).data)

    def patch(self, request, user_id=None):
        user_id = user_id or request.data.get("user_id")
        user = User.objects.filter(pk=user_id).first()
        if not user:
            return Response({"detail": "Not found."}, status=404)
        status_val = request.data.get("status")
        if status_val in User.Status.values:
            user.status = status_val
            user.save(update_fields=["status"])
        return Response(UserSerializer(user).data)


class AdminProfileModerationView(APIView):
    permission_classes = [IsPlatformAdmin]

    def get(self, request):
        status = request.query_params.get("status", NannyProfile.ModerationStatus.PENDING)
        qs = NannyProfile.objects.filter(moderation_status=status).select_related("city", "user")[:50]
        data = [
            {
                "id": p.pk,
                "name": str(p),
                "email": p.user.email,
                "city": p.city.name if p.city_id else "—",
                "status": p.moderation_status,
                "is_verified": p.is_verified,
                "hourly_rate": p.hourly_rate,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in qs
        ]
        return Response(data)

    def post(self, request):
        profile = NannyProfile.objects.filter(pk=request.data.get("profile_id")).first()
        if not profile:
            return Response({"detail": "Not found."}, status=404)
        action = request.data.get("action")
        if action == "approve":
            profile.moderation_status = NannyProfile.ModerationStatus.APPROVED
            profile.is_verified = True
            profile.user.status = User.Status.ACTIVE
            profile.documents.filter(status=NannyDocument.DocStatus.PENDING).update(
                status=NannyDocument.DocStatus.APPROVED
            )
            if profile.documents.filter(doc_type="first_aid").exists():
                profile.first_aid_course = True
            profile.user.save(update_fields=["status"])
            profile.save(update_fields=["moderation_status", "is_verified", "first_aid_course"])
        elif action == "reject":
            profile.moderation_status = NannyProfile.ModerationStatus.REJECTED
            profile.save(update_fields=["moderation_status"])
        return Response({"id": profile.pk, "status": profile.moderation_status})


class AdminDocumentsView(APIView):
    permission_classes = [IsPlatformAdmin]

    def get(self, request):
        status = request.query_params.get("status", NannyDocument.DocStatus.PENDING)
        qs = (
            NannyDocument.objects.filter(status=status)
            .select_related("nanny", "nanny__user")
            .order_by("-uploaded_at")[:50]
        )
        return Response(
            [
                {
                    "id": d.pk,
                    "nanny_id": d.nanny_id,
                    "nanny_name": str(d.nanny),
                    "email": d.nanny.user.email,
                    "doc_type": d.doc_type,
                    "doc_type_label": d.get_doc_type_display(),
                    "status": d.status,
                    "file_url": d.file.url if d.file else "",
                    "uploaded_at": d.uploaded_at.isoformat(),
                }
                for d in qs
            ]
        )

    def post(self, request):
        doc = NannyDocument.objects.filter(pk=request.data.get("document_id")).first()
        if not doc:
            return Response({"detail": "Not found."}, status=404)
        action = request.data.get("action")
        if action == "approve":
            doc.status = NannyDocument.DocStatus.APPROVED
        elif action == "reject":
            doc.status = NannyDocument.DocStatus.REJECTED
        else:
            return Response({"detail": "Invalid action."}, status=400)
        doc.save(update_fields=["status"])
        return Response({"id": doc.pk, "status": doc.status})


class AdminPaymentsView(APIView):
    permission_classes = [IsPlatformAdmin]

    def get(self, request):
        section = request.query_params.get("section", "payments")
        if section == "subscriptions":
            return Response(self._subscriptions_payload())
        if section == "commissions":
            return Response(self._commissions_payload())
        return Response(self._payments_payload())

    def _payments_payload(self):
        qs = Payment.objects.select_related("user", "plan").order_by("-created_at")[:50]
        return [
            {
                "id": p.pk,
                "order_reference": p.order_reference,
                "email": p.user.email,
                "plan": p.plan.title if p.plan_id else "—",
                "amount_uah": p.amount_uah,
                "provider": p.provider,
                "status": p.status,
                "created_at": p.created_at.isoformat(),
            }
            for p in qs
        ]

    def _subscriptions_payload(self):
        qs = (
            Subscription.objects.select_related("parent__user", "plan", "payment")
            .order_by("-started_at")[:50]
        )
        return [
            {
                "id": s.pk,
                "email": s.parent.user.email,
                "plan": s.plan.title if s.plan_id else "—",
                "status": s.status,
                "contacts_remaining": s.contacts_remaining,
                "city_access_until": s.city_access_until.isoformat() if s.city_access_until else None,
                "started_at": s.started_at.isoformat(),
            }
            for s in qs
        ]

    def _commissions_payload(self):
        from django.conf import settings

        rate = getattr(settings, "PLATFORM_COMMISSION_RATE", 0.1)
        paid = Payment.objects.filter(status=Payment.Status.PAID)
        total_revenue = paid.aggregate(total=Sum("amount_uah"))["total"] or 0
        commission_total = int(total_revenue * rate)
        rows = paid.select_related("user", "plan").order_by("-created_at")[:50]
        return {
            "rate_percent": int(rate * 100),
            "commission_total_uah": commission_total,
            "revenue_total_uah": total_revenue,
            "items": [
                {
                    "order_reference": p.order_reference,
                    "email": p.user.email,
                    "amount_uah": p.amount_uah,
                    "commission_uah": int(p.amount_uah * rate),
                    "created_at": p.created_at.isoformat(),
                }
                for p in rows
            ],
        }


class AdminAnalyticsView(APIView):
    permission_classes = [IsPlatformAdmin]

    def get(self, request):
        now = timezone.now()
        today = now.date()
        month_ago = now - timezone.timedelta(days=30)
        day_ago = now - timezone.timedelta(days=1)

        six_months_ago = now - timezone.timedelta(days=180)
        paid_by_month = (
            Payment.objects.filter(status=Payment.Status.PAID, created_at__gte=six_months_ago)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(revenue=Sum("amount_uah"), count=Count("id"))
            .order_by("month")
        )
        months = [
            {
                "label": row["month"].strftime("%b %Y") if row["month"] else "—",
                "revenue": row["revenue"] or 0,
                "count": row["count"],
            }
            for row in paid_by_month
        ]

        parents_count = ParentProfile.objects.count()
        paid_users = (
            Payment.objects.filter(status=Payment.Status.PAID)
            .values("user")
            .distinct()
            .count()
        )
        funnel = {
            "users": User.objects.count(),
            "parents": parents_count,
            "nannies": NannyProfile.objects.count(),
            "verified_nannies": NannyProfile.objects.filter(is_verified=True).count(),
            "paid_users": paid_users,
        }

        dau = User.objects.filter(last_login__date=today).count()
        mau = User.objects.filter(last_login__gte=month_ago).count()
        conversion = round((paid_users / parents_count) * 100, 1) if parents_count else 0

        daily_active = (
            User.objects.filter(last_login__gte=day_ago)
            .annotate(day=TruncDay("last_login"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("-day")[:14]
        )
        activity = [
            {
                "label": row["day"].strftime("%d.%m") if row["day"] else "—",
                "count": row["count"],
            }
            for row in daily_active
        ]

        roles = User.objects.values("role").annotate(count=Count("id"))
        return Response(
            {
                "months": months,
                "funnel": funnel,
                "roles": list(roles),
                "dau": dau,
                "mau": mau,
                "conversion_percent": conversion,
                "activity": activity,
            }
        )
