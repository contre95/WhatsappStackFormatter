# WhatsApp Cloudformation stack formatter

This Python script formats the stack taken from [this website](https://developers.facebook.com/docs/whatsapp/changelog) so that it does not creates IAM resources but uses already existing ones instead.

This scripts removes every IAM Resource created in the stack and aim to use the same stack with the following standard.

In case a `AWS::IAM::Role` is created like so:
```yaml
# ...
  ECSScalingRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
        - Effect: Allow
          Principal:
            Service:
              - ecs.amazonaws.com
          Action:
            - 'sts:AssumeRole'
      Path: /whatsapp/
# ...

```

Then the resources that make reference to that `Role` will now use the *supposedly* existing role under the following standard:
`arn:aws:iam::` + **AWS_ACCOUNT_NUMBER** + `:role/ECSScalingRole` + **CUSTOM_POSTFIX** 
So make sure to have those created before deploying the stack. 
Both the *AWS_ACCOUNT_NUMBER* and the *CUSTOM_POSTFIX* can be configured inside the `main.py` file
                                                                                            

## Install 
```shell
python -m venv venv
pip install -r req.txt
```

## Run
```shell
 cat wa_ent_example.yml | cfn-flip | ./main.py | cfn-flip > formatted_wa_ent_example.yml
```
