import pulumi
import pulumi_aws as aws
import json


#Environment variable file
with open("./../../config.json") as config_file:
    data = json.load(config_file)

ORGANIZATION_ID = data["ORGANIZATION_ID"]
KMS_KEY = aws.kms.get_key(key_id=f"alias/kms-sharedbackups")

# non-prod vault
sharedbackups_vault_nonprod = aws.backup.Vault(
    "sharedbackups-vault-nonprod",
    name="sharedbackups-vault-nonprod",
    kms_key_arn=KMS_KEY.arn,
    tags={
        "ENVIRONMENT": "nonprod",
        "Name": "sharedbackups-vault-nonprod",
        "BUSINESS_UNIT": "Security",
        "SUPPORT_EMAIL": "abc@xyz.com",
        "PRIVACY": "high",
    },
)

sharedbackups_vault_nonprod_policy = aws.backup.VaultPolicy(
    "sharedbackups-vault-nonprod-policy",
    backup_vault_name=sharedbackups_vault_nonprod.name,
    policy=sharedbackups_vault_nonprod.arn.apply(
        lambda arn: f"""{{
  "Version": "2012-10-17",
  "Id": "default",
  "Statement": [
    {{
      "Sid": "default",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "backup:CopyIntoBackupVault",
      "Resource": "*",
      "Condition": {{
          "StringEquals": {{
              "aws:PrincipalOrgID": [
                  "{ORGANIZATION_ID}"
              ]
          }}
      }}
    }}
  ]
}}
"""
    ),
)


# prod vault
sharedbackups_vault_prod = aws.backup.Vault(
    "sharedbackups-vault-prod",
    name="sharedbackups-vault-prod",
    kms_key_arn=KMS_KEY.arn,
    tags={
        "ENVIRONMENT": "prod",
        "Name": "sharedbackups-vault-prod",
        "BUSINESS_UNIT": "Security",
        "SUPPORT_EMAIL": "abc@xyz.com",
        "PRIVACY": "high",
    },
)

sharedbackups_vault_prod_policy = aws.backup.VaultPolicy(
    "sharedbackups-vault-prod-policy",
    backup_vault_name=sharedbackups_vault_prod.name,
    policy=sharedbackups_vault_prod.arn.apply(
        lambda arn: f"""{{
  "Version": "2012-10-17",
  "Id": "default",
  "Statement": [
    {{
      "Sid": "default",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "backup:CopyIntoBackupVault",
      "Resource": "*",
      "Condition": {{
          "StringEquals": {{
              "aws:PrincipalOrgID": [
                  "{ORGANIZATION_ID}"
              ]
          }}
      }}
    }}
  ]
}}
"""
    ),
)

backups_service_role = aws.iam.Role(
    f"backups-service-role",
    name=f"backups-service-role",
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Effect": "Allow",
                    "Sid": "",
                    "Principal": {
                        "Service": "backup.amazonaws.com",
                    },
                }
            ],
        }
    ),
    managed_policy_arns=[
        "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForBackup",
        "arn:aws:iam::aws:policy/service-role/AWSBackupServiceRolePolicyForRestores",
    ],
    tags={
        "ENVIRONMENT": "sharedbackups",
        "Name": "backups-service-role",
        "BUSINESS_UNIT": "Security",
        "SUPPORT_EMAIL": "abc@xyz.com",
        "PRIVACY": "high",
    },
)