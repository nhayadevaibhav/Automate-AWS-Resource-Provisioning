import boto3
import os
import json
import mimetypes
import sys

# ===== CONFIG =====
bucket_name = sys.argv[1] if len(sys.argv) > 1 else "my-static-site-vaibhav-123"
region = "ap-south-1"
folder_path = "website"

# ===== INIT S3 CLIENT =====
s3 = boto3.client("s3", region_name=region)

# ===== CREATE BUCKET =====
print("Creating bucket...")
try:
    s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={"LocationConstraint": region}
    )
except Exception as e:
    print("Bucket may already exist:", e)

# ===== DISABLE BLOCK PUBLIC ACCESS =====
print("Setting public access...")
s3.put_public_access_block(
    Bucket=bucket_name,
    PublicAccessBlockConfiguration={
        "BlockPublicAcls": False,
        "IgnorePublicAcls": False,
        "BlockPublicPolicy": False,
        "RestrictPublicBuckets": False
    }
)

# ===== ADD BUCKET POLICY =====
print("Applying bucket policy...")
policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": ["s3:GetObject"],
            "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
        }
    ]
}

s3.put_bucket_policy(
    Bucket=bucket_name,
    Policy=json.dumps(policy)
)

# ===== ENABLE STATIC WEBSITE =====
print("Enabling static website hosting...")
s3.put_bucket_website(
    Bucket=bucket_name,
    WebsiteConfiguration={
        "IndexDocument": {"Suffix": "index.html"},
        "ErrorDocument": {"Key": "index.html"}
    }
)

# ===== UPLOAD FILES =====
print("Uploading files...")
for root, dirs, files in os.walk(folder_path):
    for file in files:
        file_path = os.path.join(root, file)
        content_type = mimetypes.guess_type(file_path)[0] or "text/plain"

        s3.upload_file(
            file_path,
            bucket_name,
            file,
            ExtraArgs={"ContentType": content_type}
        )
        print(f"Uploaded: {file}")

# ===== WEBSITE URL =====
website_url = f"http://{bucket_name}.s3-website-{region}.amazonaws.com"

print("\n DEPLOYMENT COMPLETE")
print("Website URL:", website_url)