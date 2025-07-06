from tortoise import fields, models


class AccountModel(models.Model):
    id = fields.IntField(pk=True)
    phone = fields.CharField(max_length=32, unique=True)
    session_file = fields.CharField(max_length=255)

    # 0=>正常 1=>无效
    status = fields.SmallIntField(default=0)
    flood_expire_at = fields.DatetimeField(null=True)
    daily_boost_count = fields.IntField(default=0)

    # 0=>就绪 1=>使用中
    using_status = fields.SmallIntField(default=0)
    last_used_at = fields.DatetimeField(auto_now_add=True)

    is_deleted = fields.BooleanField(default=False)

    frozen_at = fields.DateField(null=True)

    def __str__(self):
        return self.phone

    class Meta:
        table = "account"


class BoostLinkModel(models.Model):
    id = fields.IntField(pk=True)
    link = fields.CharField(max_length=255, unique=True)
    bot = fields.CharField(max_length=255)
    command = fields.CharField(max_length=255)
    param = fields.CharField(max_length=255)

    is_deleted = fields.BooleanField(default=False)

    def __str__(self):
        return self.link

    class Meta:
        table = "boost_link"


class BoostLinkAccountUsageModel(models.Model):
    id = fields.IntField(pk=True)
    boost_link_id = fields.IntField()
    account_id = fields.IntField()
    boost_at = fields.DateField(auto_now_add=True)

    class Meta:
        table = "boost_link_account_usage"


class BoostLogModel(models.Model):
    id = fields.IntField(pk=True)
    account_id = fields.IntField()
    boost_link_id = fields.IntField()

    # 0=>助力成功 1=>重复助力 2=>账号超过助力次数
    status = fields.SmallIntField(default=0)

    class Meta:
        table = "boost_log"


class CampaignModel(models.Model):
    id = fields.IntField(pk=True)
    boost_link_id = fields.IntField()

    # 0=> 已就绪 1=>进行中 2=>已完成
    status = fields.SmallIntField(default=0)
    total_assigned = fields.IntField(default=0)
    success_count = fields.IntField(default=0)
    fail_count = fields.IntField(default=0)
    repeat_count = fields.IntField(default=0)
    requested_at = fields.DatetimeField(null=True)

    class Meta:
        table = "campaign"
