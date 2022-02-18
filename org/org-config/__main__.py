import pulumi_aws as aws
from pulumi import ResourceOptions


sydney_region = aws.Provider(
    "ap-southeast-2", profile=aws.config.profile, region="ap-southeast-2"
)

enable_cross_account_management = aws.backup.GlobalSettings(
    "enable-cross-account-management",
    global_settings={
        "isCrossAccountBackupEnabled": "true",
    },
    opts=ResourceOptions(provider=sydney_region),
)