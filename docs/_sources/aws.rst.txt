Amazon Web Services
===================

How Startifact uses your account
--------------------------------

Startifact stores artifacts and metadata in S3 buckets that you must deploy yourself.

Startifact stores your :ref:`organisation configuration <Organisation configuration>` and the version numbers of staged artifacts in Systems Manager parameters that Startifact manages.

Region preparation
------------------

Startifact hates to keep all of your eggs in one basket. And so, Startifact will balance across as many regions as you like. If a region goes down, Startifact will automatically use another.

Each region must have:

1. An S3 bucket.
2. A Systems Manager parameter where the bucket's name can be read. `Why do you care what your S3 buckets are named? <https://unbuild.blog/2021/12/why-do-you-care-what-your-s3-buckets-are-named/>`_ explains why Startifact is opinionated on this.

The Systems Manager parameter that holds the bucket's name must be the same in every region that Startifact will use. If you name it, say, ``/MyPlatform/Buckets/Staging`` in one region then it *must* also be named ``/MyPlatform/Buckets/Staging`` in all other regions.

S3 bucket and parameter
-----------------------

Here's a complete CloudFormation template you can copy and deploy:

.. code-block:: yaml

  Description: Artifact storage
  Resources:
    Artifacts:
      Type: AWS::S3::Bucket
      Properties:
        PublicAccessBlockConfiguration:
          BlockPublicAcls: true
          BlockPublicPolicy: true
          IgnorePublicAcls: true
          RestrictPublicBuckets: true

    ArtifactsParameter:
      Type: AWS::SSM::Parameter
      Properties:
        # The parameter can be named anything you want, but
        # remember it for the organisation setup script:
        Name: /Buckets/Staging
        Type: String
        Value:
          Ref: Artifacts

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
