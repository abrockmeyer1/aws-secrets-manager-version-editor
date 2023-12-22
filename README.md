# Secrets Manager Version Editor
This directory is designed to be used by admins from local environments to make updates to secrets.
It should be used in place of the AWS UI which does not support version history management.
This Repository will automatically create a version label with a timestamp when used. If you wish to change this behavior, you can edit the stage label using directions below.

<!--ts-->
   * [](#requirements)
   * [](#how-to-use)
   * [](#examples)
      * [](#1-creating-a-new-secret)
      * [](#2-deleting-a-secret)
      * [](#3-get-value-of-a-secret)
      * [](#4-list-secret-version-ids-for-a-secret)
      * [](#5-list-secrets-ids-from-secrets-manager)
      * [](#6-restore-a-secret-within-the-recovery-window)
      * [](#7-update-value-of-a-secret)
      * [](#8-update-secret-version-stage-labels---controlling-version-history)

<!-- Created by https://github.com/ekalinin/github-markdown-toc -->
<!-- Added by: abroc, at: Fri, Dec 22, 2023  3:33:36 PM -->

<!--te-->

## Requirements
- AWS CLI Programmatic Access
- IAM Access to Secrets Manager
- Python3.7 or greater
- Pip installed

## How to Use
1. clone the repo and use the following command to enter the smts-secrets directory
```
cd smts-secrets
```

2. Run the install either in virtual environment or in local
For virtual environments or testing:
```
python -m venv venv
source venv/bin/activate
python -m pip install .
```
```
python -m pip install . --user
```

3. Set your AWS_PROFILE environment variable and run the smts-secrets command below
```
export AWS_PROFILE=<aws_profile> 

(this step isn't necessary, but will be easier 
than supplying the --profile flag for every call)

smts-secrets --help
```

You should see text like shown below:
```
$ smts-secrets --help
Usage: smts-secrets [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  create-secret                Create a Secret
  delete-secret                Delete a Secret, default recovery window is 7
                               days, use --force to delete immediately
  get-secret-value             Get Value of a Secret
  list-secret-versions         List Secret Version IDs for a Secret and get
                               their Stage Labels
  list-secrets                 List Secrets Ids from Secrets Manager
  restore-secret               Restore a Secret within the recovery window
  update-secret-value          Update Value of a Secret
  update-secret-version-stage  Update Secret Version Stage Labels
```

For additional information on the commands, run ```smts-secrets <command> --help```

## Examples:
### 1. Creating a new Secret
```
$ smts-secrets create-secret --help
Usage: smts-secrets create-secret [OPTIONS]

  Used to create a new secret in secrets manager and add a version stage label
  to the secret version id

Options:
  -r, --region TEXT     AWS Region to use  [default: us-gov-west-1]
  -p, --profile TEXT    AWS Profile to use  [default: default]
  --sid TEXT            Secret ID to use  [required]
  --secret-string TEXT  Secret String to use
  --secret-file TEXT    Secret File to use
  --help                Show this message and exit.
```
***With a secret string***
```
$ smts-secrets create-secret \
    --profile <aws_profile_name> \
    --sid my-new-secret \
    --secret-string "my new secret text"
```
***With a json document of secrets***
```
$ smts-secrets create-secret \
    --profile <aws_profile_name> \
    --sid my-new-secret \
    --secret-file secret_file.json
```

### 2. Deleting A Secret
```
$ smts-secrets delete-secret --help
Usage: smts-secrets delete-secret [OPTIONS]

  Delete a Secret, default recovery window is 7 days, use --force to delete
  immediately

Options:
  --force                     Force Immediate Deletion of Secret
  -rw, --recv-window INTEGER  Recovery Window in Days
  -r, --region TEXT           AWS Region to use  [default: us-gov-west-1]
  -p, --profile TEXT          AWS Profile to use  [default: default]
  --sid TEXT                  Secret ID to use  [required]
  --help                      Show this message and exit.
```
***By Setting a Recovery Window***
```
$ smts-secrets delete-secret \
    --profile <aws_profile_name> \
    --sid existing-secret-name \
    --recv-window 9

Secret Scheduled for Deletion: Recovery Window is 8 days
```
***By Sheduling Immediate Deletion (Unrecoverable)***
```
$ smts-secrets delete-secret \
    --profile <aws_profile_name> \
    --sid existing-secret-name \
    --force

Secret deleted
```

### 3. Get Value of a Secret
```
$ smts-secrets get-secret-value --help
Usage: smts-secrets get-secret-value [OPTIONS]

Options:
  --vid TEXT          Secret Version ID to use (required for old versions)
  -o, --output TEXT   Output File
  -r, --region TEXT   AWS Region to use  [default: us-gov-west-1]
  -p, --profile TEXT  AWS Profile to use  [default: default]
  --sid TEXT          Secret ID to use  [required]
  --help              Show this message and exit
```
***Get Secret Value***
```
smts-secrets get-secret-value \
    --sid <secret_id>
```
***Get Previous Version Secret Value***
```
smts-secrets get-secret-value \
    --sid <secret_id> \
    --vid <secret_version_id>
```
### 4. List Secret Version IDs for a Secret
```
$ smts-secrets list-secret-versions --help
Usage: smts-secrets list-secret-versions [OPTIONS]

  List Secret Version IDs for a Secret and get their Stage Labels

Options:
  -r, --region TEXT   AWS Region to use  [default: us-gov-west-1]
  -p, --profile TEXT  AWS Profile to use  [default: default]
  --sid TEXT          Secret ID to use  [required]
  --help              Show this message and exit.
```
```
smts-secrets list-secret-versions \
    --sid <secret_id>
```
### 5. List Secrets Ids from Secrets Manager
```
$ smts-secrets list-secrets --help
Usage: smts-secrets list-secrets [OPTIONS]

  List Secrets Ids from Secrets Manager

Options:
  -r, --region TEXT   AWS Region to use  [default: us-gov-west-1]
  -p, --profile TEXT  AWS Profile to use  [default: default]
  --help              Show this message and exit.
```
```
smts-secrets list-secrets
```
### 6. Restore a Secret within the recovery window
```
$ smts-secrets restore-secret --help
Usage: smts-secrets restore-secret [OPTIONS]

  Restore a Secret within the recovery window

Options:
  -r, --region TEXT   AWS Region to use  [default: us-gov-west-1]
  -p, --profile TEXT  AWS Profile to use  [default: default]
  --sid TEXT          Secret ID to use  [required]
  --help              Show this message and exit.
```
```
smts-secrets restore-secret \
    --sid <secret_id>
```
### 7. Update Value of a Secret
```
$ smts-secrets update-secret-value --help
Usage: smts-secrets update-secret-value [OPTIONS]

Options:
  -r, --region TEXT     AWS Region to use  [default: us-gov-west-1]
  -p, --profile TEXT    AWS Profile to use  [default: default]
  --sid TEXT            Secret ID to use  [required]
  --secret-string TEXT  Secret String to use
  --secret-file TEXT    Secret File to use
  --help                Show this message and exit.
```
***Update Secret with Secret String***
```
smts-secrets update-secret-value \
    --sid <secret_id> \
    --secret-string '<secret_string>'
```
***Update Secret with Secret File***
```
smts-secrets update-secret-value \
    --sid <secret_id> \
    --secret-file '<secret_filename>'
```
### 8. Update Secret Version Stage Labels - Controlling Version History
>:point_up: **This can be used to revert to a prior version of a secret**

```
$ smts-secrets update-secret-version-stage --help
Usage: smts-secrets update-secret-version-stage [OPTIONS]

  Use Cases:
  1. Remove label from a secret version id
  2. Add label to a secret version id
  3. Remove label from one secret version id and add to another secret version id

  How to use:
  Use Case 1:
  smts-secrets update-secret-version-stage --sid <secret-id> --stage-label <stage-label> --from-vid <version-id>
  Use Case 2:
  smts-secrets update-secret-version-stage --sid <secret-id> --stage-label <stage-label> --to-vid <version-id>
  Use Case 3:
  smts-secrets update-secret-version-stage --sid <secret-id> --stage-label <stage-label> --from-vid <version-id> --to-vid <version-id>

Options:
  -f, --from-vid TEXT      Label will be removed from this Secret Version ID
  -t, --to-vid TEXT        Label will be added to this Secret Version ID,
                           label must not exist on another id
  -sl, --stage-label TEXT  Secret Version Stage to use  [required]
  -r, --region TEXT        AWS Region to use  [default: us-gov-west-1]
  -p, --profile TEXT       AWS Profile to use  [default: default]
  --sid TEXT               Secret ID to use  [required]
  --help                   Show this message and exit.
```

***To Revert to prior version of secret***
```
smts-secrets update-secret-version-stage \
    --sid <secret_id> \
    --stage-lable 'AWSCURRENT' \
    --from-vid <current version id with AWSCURRENT applied> \
    --to-vid <old version id to revert to>
```
***To Move Version Label***
> :warning: **version stages without labels are removed from history**
```
smts-secrets update-secret-version-stage \
    --sid <secret_id> \
    --stage-lable '<stage lable to move>' \
    --from-vid <current version id with stage label applied> \
    --to-vid <old version id to remove label from>
```
***To add new stage label***
```
smts-secrets update-secret-version-stage \
    --sid <secret_id> \
    --stage-lable '<stage_label>' \
    --to-vid <version id to apply label to>
```
***To remove stage label***
> :warning: **version stages without labels are removed from history**
```
smts-secrets update-secret-version-stage \
    --sid <secret_id> \
    --stage-lable '<stage_label>' \
    --from-vid <version id with stage_label>
```