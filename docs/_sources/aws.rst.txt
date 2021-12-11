Amazon Web Services
===================

How Startifact uses your account
--------------------------------

Startifact stores artifacts and metadata in an S3 bucket that you must deploy yourself.

Startifact stores your :ref:`organisation configuration <Organisation configuration>` and the version numbers of staged artifacts in Systems Manager parameters that Startifact manages.

S3 bucket
---------

Startifact will not deploy an S3 bucket for you. You must deploy and own the security yourself.

Startifact requires your bucket's name to be readable from a Systems Manager parameter. This allows you to deploy a bucket without a hard-coded name that's still discoverable. `Why do you care what your S3 buckets are named? <https://unbuild.blog/2021/12/why-do-you-care-what-your-s3-buckets-are-named/>`_ explains why Startifact is opinionated.

Here's a complete CloudFormation template you can copy and deploy:

.. code-block:: yaml

  Description: Artifact storage
  Resources:
    Bucket:
      Type: AWS::S3::Bucket
      Properties:
        PublicAccessBlockConfiguration:
          BlockPublicAcls: true
          BlockPublicPolicy: true
          IgnorePublicAcls: true
          RestrictPublicBuckets: true

    BucketParameter:
      Type: AWS::SSM::Parameter
      Properties:
        # This name can be anything you want:
        Name: /artifacts-bucket
        Type: String
        Value:
          Ref: Bucket

IAM policies
------------

The user performing the one-time :ref:`organisation setup <Organisation configuration>` must be granted:

- ``ssm:GetParameter`` and ``ssm:PutParameter`` on the configuration parameter. This is ``arn:aws:ssm:{REGION}:{ACCOUNT ID}:parameter/Startifact`` by default, but adjust if you are using a different parameter name.

Any identities that download artifacts must be granted:

- ``ssm:GetParameter`` on the configuration parameter.
- ``ssm:GetParameter`` on the bucket name parameter.
- ``ssm:GetParameter`` on every parameter beneath the name prefix (or *all* parameters if you have no name prefix).
- ``s3:GetObject`` on every S3 object in the artifacts bucket beneath the key prefix (or *all* objects if you have no key prefix).
- Optional: ``s3:PutObject`` on S3 keys ending with ``*/metadata`` to allow appending metadata to existing artifacts.

Any identities that stage artifacts must be granted:

- ``ssm:GetParameter`` on the configuration parameter.
- ``ssm:GetParameter`` on the bucket name parameter.
- ``ssm:PutParameter`` on every parameter beneath the name prefix (or *all* parameters if you have no name prefix).
- ``s3:ListBucket`` on the artifacts bucket.
- ``s3:PutObject`` on every S3 object in the artifacts bucket beneath the key prefix (or *all* objects if you have no key prefix).
