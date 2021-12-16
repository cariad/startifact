Amazon Web Services
===================

How Startifact uses your account
--------------------------------

Startifact stores artifacts and metadata in S3 buckets that you must deploy yourself.

Startifact stores your :ref:`organisation configuration <Organisation configuration>` and the version numbers of staged artifacts in Systems Manager parameters that Startifact manages.

Startifact will balance between as many regions as you care to prepare.

Your region preparation
-------------------------

Each region must have:

* An S3 bucket.
* A Systems Manager parameter that holds the bucket's name. `Why do you care what your S3 buckets are named? <https://unbuild.blog/2021/12/why-do-you-care-what-your-s3-buckets-are-named/>`_ explains why Startifact is opinionated.

.. note::
   This Systems Manager parameter must have the same name in every region. If you name it ``/buckets/staging`` in one region then it must be named ``/buckets/staging`` in *all* regions.

What Startifact creates in each region
--------------------------------------

When you complete the :ref:`organisation configuration <Organisation configuration>`, Startifact will create a Systems Manager parameter named ``/startifact`` to hold your preferences.

.. tip::
  You change the name of this parameter by setting the ``STARTIFACT_PARAMETER`` environment variable.

  Take care, however, that you set that variable on *every* machine that Startifact runs on.

When you stage an artifact, Startifact will:

- Upload the artifact file and metadata to your S3 bucket.
- Create or update a Systems Manager parameter per-project to record the latest version.


Regional IAM policies
---------------------

The user performing the one-time :ref:`organisation setup <Organisation configuration>` must be granted ``ssm:GetParameter`` and ``ssm:PutParameter`` on the configuration parameter.

Any identities that download artifacts must be granted:

* ``ssm:GetParameter`` on:

  * The configuration parameter

  * The bucket name parameter

  * Every parameter beneath the name prefix (or *all* parameters if you have no name prefix).

* ``s3:GetObject`` on every S3 object in the artifacts bucket beneath the key prefix (or *all* objects if you have no key prefix).

.. note::
  The parameter name prefix and S3 key prefix are optional and configured during the :ref:`organisation setup <Organisation configuration>` process.

Any identities that stage artifacts must be granted:

* ``ssm:GetParameter`` on:

  * The configuration parameter

  * The bucket name parameter

* ``ssm:PutParameter`` on every parameter beneath the name prefix (or *all* parameters if you have no name prefix).

* ``s3:ListBucket`` on the artifacts bucket.

* ``s3:PutObject`` on every S3 object in the artifacts bucket beneath the key prefix (or *all* objects if you have no key prefix).

CloudFormation template
-----------------------

Here's a complete CloudFormation template you can copy to deploy an S3 bucket, Systems Manager parameter, and managed policies for access:

.. code-block:: yaml

   Description: Artifact staging

   Parameters:
     ArtifactParameterNamePrefix:
       Default: /artifacts
       Type: String

     BucketKeyPrefix:
       Default: ""  # e.g. "prefix/"
       Type: String

     BucketParameterName:
       Default: /buckets/staging
       Type: String

     StartifactConfigurationParameterName:
       Default: /startifact
       Type: String

   Resources:
     Staging:
       Type: AWS::S3::Bucket
       Properties:
         PublicAccessBlockConfiguration:
           BlockPublicAcls: true
           BlockPublicPolicy: true
           IgnorePublicAcls: true
           RestrictPublicBuckets: true

     StagingParameter:
       Type: AWS::SSM::Parameter
       Properties:
         Name:
           Ref: BucketParameterName
         Type: String
         Value:
           Ref: Staging

     AllowRead:
       Type: AWS::IAM::ManagedPolicy
       Properties:
         Description: Read-only access to staged artifacts
         PolicyDocument:
           Version: 2012-10-17
           Statement:
             - Action:
                 - s3:GetObject
               Effect: Allow
               Resource:
                 # Allowed to download artifact files and metadata:
                 - Fn::Sub: arn:aws:s3:::${Staging}/${BucketKeyPrefix}*

             - Action:
                 - ssm:GetParameter
               Effect: Allow
               Resource:
                 # Allowed to read configuration:
                 - Fn::Sub: arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:parameter${StartifactConfigurationParameterName}
                 # Allowed to read the name of the bucket:
                 - Fn::Sub: arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:parameter${BucketParameterName}
                 # Allowed to read artifact versions:
                 - Fn::Sub: arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:parameter${ArtifactParameterNamePrefix}*

     AllowWrite:
       Type: AWS::IAM::ManagedPolicy
       Properties:
         Description: Write-only access to staged artifacts
         PolicyDocument:
           Version: 2012-10-17
           Statement:
             - Action:
                 - s3:ListBucket
               Effect: Allow
               Resource:
                 # Allowed to check if an artifact has already been uploaded:
                 - Fn::Sub: arn:aws:s3:::${Staging}

             - Action:
                 - s3:PutObject
               Effect: Allow
               Resource:
                 # Allowed to upload artifact files and metadata:
                 - Fn::Sub: arn:aws:s3:::${Staging}/${BucketKeyPrefix}*

             - Action:
                 - ssm:GetParameter
               Effect: Allow
               Resource:
                 # Allowed to read configuration:
                 - Fn::Sub: arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:parameter${StartifactConfigurationParameterName}
                 # Allowed to read the name of the bucket:
                 - Fn::Sub: arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:parameter${BucketParameterName}

             - Action:
                 - ssm:PutParameter
               Effect: Allow
               Resource:
                 # Allowed to write artifact versions:
                 - Fn::Sub: arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:parameter${ArtifactParameterNamePrefix}*

     AllowConfigure:
       Type: AWS::IAM::ManagedPolicy
       Properties:
         Description: Grants permission to configure Startifact
         PolicyDocument:
           Version: 2012-10-17
           Statement:
             - Action:
                 - ssm:GetParameter
                 - ssm:PutParameter
               Effect: Allow
               Resource:
                 # Allowed to read and write configuration:
                 - Fn::Sub: arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:parameter${StartifactConfigurationParameterName}
