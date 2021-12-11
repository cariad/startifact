Examples
========

Staging then deploying a lambda function
----------------------------------------

This example assumes you'll be deploying your code via a CloudFormation template like this:

.. code-block:: yaml

   Parameters:

   BuildBucket:
      Type: String

   BuildKey:
      Type: String

   BuildHash:
      Type: String

   Resources:

   Function:
      Type: AWS::Lambda::Function
      Properties:
         Code:
         S3Bucket:
            Ref: BuildBucket
         S3Key:
            Ref: BuildKey

   FunctionVersion:
      Type: AWS::Lambda::Version
      Properties:
         CodeSha256:
         Ref: BuildHash
         FunctionName:
         Ref: Function

When you're ready to stage your code:

1. Package it as a zip.
2. Attach the hash as metadata.

.. code-block:: console

   hash="$(openssl dgst -sha256 -binary dist.zip | openssl enc -base64)"
   startifact MyLambdaProject 1.0.1 --stage dist.zip --metadata "hash=${hash:?}"

Now, to populate your CloudFormation template's parameters:

1. Create a Startifact session.
2. ``get()`` the artifact to deploy.
3. Read the artifact's ``bucket``, ``key`` and metadata.

.. code-block:: python

   from startifact import Session

   session = Session()
   artifact = session.get("MyLambdaProject", "1.0.1")

   params.add("BuildBucket", artifact.bucket)
   params.add("BuildKey", artifact.key)
   params.add("BuildHash", artifact["hash"])
