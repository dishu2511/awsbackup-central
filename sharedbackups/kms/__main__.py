import json
import pulumi_aws as aws


#Environment variable file
with open("./../../config.json") as config_file:
    data = json.load(config_file)


ENV = "sharedbackups"    
ENV_ACCOUNT = data['ACCOUNT'][ENV.upper()]['ID']
DEV_ACCOUNT = data['ACCOUNT']['DEV']['ID']
PROD_ACCOUNT = data['ACCOUNT']['PROD']['ID']
IAM_USER = data["IAM_USER"]


key = aws.kms.Key(
    f"kms-{ENV}",
    deletion_window_in_days=30,
    description="CMK kms key",
    tags={
        "ENVIRONMENT": ENV,
        "Name": f"kms-{ENV}",
        "BUSINESS_UNIT": "Security",
        "SUPPORT_EMAIL": "abc@xyz.com",
        "PRIVACY": "high",
    },
    policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Id": "key-consolepolicy",
            "Statement": [
                {
                    "Sid": "Enable IAM User Permissions",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": "arn:aws:iam::{}:root".format(ENV_ACCOUNT)
                        },
                    "Action": "kms:*",
                    "Resource": "*",
                },
                {
                    "Sid": "Allow access for Key Administrators",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": [
                            f"arn:aws:iam::{ENV_ACCOUNT}:user/{IAM_USER}",
                            f"arn:aws:iam::{ENV_ACCOUNT}:role/backups-service-role"
                        ]
                    },
                    "Action": [
                        "kms:Create*",
                        "kms:Describe*",
                        "kms:Enable*",
                        "kms:List*",
                        "kms:Put*",
                        "kms:Update*",
                        "kms:Revoke*",
                        "kms:Disable*",
                        "kms:Get*",
                        "kms:Delete*",
                        "kms:TagResource",
                        "kms:UntagResource",
                        "kms:ScheduleKeyDeletion",
                        "kms:CancelKeyDeletion",
                    ],
                    "Resource": "*",
                },
                {
                    "Sid": "Allow use of the key",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": [
                            f"arn:aws:iam::{ENV_ACCOUNT}:root"
                        ]
                    },
                    "Action": [
                        "kms:Encrypt",
                        "kms:Decrypt",
                        "kms:ReEncrypt*",
                        "kms:GenerateDataKey*",
                        "kms:DescribeKey",
                    ],
                    "Resource": "*",
                },
                {
                    "Sid": "Allow attachment of persistent resources",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": [
                            f"arn:aws:iam::{ENV_ACCOUNT}:root",
                            f"arn:aws:iam::{DEV_ACCOUNT}:root"
                        ]
                    },
                    "Action": ["kms:CreateGrant", "kms:ListGrants", "kms:RevokeGrant"],
                    "Resource": "*",
                    "Condition": {"Bool": {"kms:GrantIsForAWSResource": "true"}},
                },
                {
                    "Sid": "Allow access through Backup for all principals in the account that are authorized to use Backup Storage",
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": [
                        "kms:CreateGrant",
                        "kms:Decrypt",
                        "kms:GenerateDataKey*",
                        "kms:DescribeKey",
                    ],
                    "Resource": "*",
                    "Condition": {
                        "StringEquals": {
                            "kms:CallerAccount": f"{ENV_ACCOUNT}",
                            "kms:ViaService": "backup.ap-southeast-2.amazonaws.com",
                        }
                    },
                },
                
                
        {
            "Sid": "Allow use of the key",
            "Effect": "Allow",
            "Principal": {
                "AWS": [
                    f"arn:aws:iam::{DEV_ACCOUNT}:root",
                    f"arn:aws:iam::{PROD_ACCOUNT}:root"
                ]
            },
            "Action": [
                "kms:Encrypt",
                "kms:Decrypt",
                "kms:ReEncrypt*",
                "kms:GenerateDataKey*",
                "kms:DescribeKey"
            ],
            "Resource": "*"
        },
        {
            "Sid": "Allow attachment of persistent resources",
            "Effect": "Allow",
            "Principal": {
                "AWS": [
                    f"arn:aws:iam::{DEV_ACCOUNT}:root",
                    f"arn:aws:iam::{PROD_ACCOUNT}:root"
                ]
            },
            "Action": [
                "kms:CreateGrant",
                "kms:ListGrants",
                "kms:RevokeGrant"
            ],
            "Resource": "*",
            "Condition": {
                "Bool": {
                    "kms:GrantIsForAWSResource": "true"
                }
            }
        }
            ],
        }
    ),
)

# creating kms key alias
alias = aws.kms.Alias(
    "alias", target_key_id=key.key_id, name=f"alias/kms-{ENV}"
)