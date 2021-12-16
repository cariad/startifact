Use cases
=========

Staging then deploying a lambda function
----------------------------------------

This example assumes you deploy your code via a CloudFormation template like this:

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

   $ hash="$(openssl dgst -sha256 -binary dist.zip | openssl enc -base64)"
   $ startifact MyLambdaProject 1.0.1 --stage dist.zip --metadata "hash=${hash:?}"

Now, to populate your CloudFormation template's parameters:

1. Create a Startifact session. Since Lambda requires the function and its code to reside in the same region, you can restrict the session to your deployment region by passing it as ``regions=["<region>"]``.
2. ``get()`` the artifact to deploy.
3. Read the artifact's ``bucket`` and ``key`` via its ``downloader``.
4. Read the artifact's hash from its metadata.

.. code-block:: python

   from startifact import Session

   session = Session(regions=["us-east-1"])
   artifact = session.get("MyLambdaProject", "1.0.1")

   params.add("BuildBucket", artifact.downloader.bucket)
   params.add("BuildKey", artifact.downloader.key)
   params.add("BuildHash", artifact["hash"])
