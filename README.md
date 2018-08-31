# alfred-workflow-jenkins-helper

Support view Jenkins Jobs status &amp; Tigger Build Job


if Mac OSX and Homebrew:
```sh
touch .pydistutils.cfg
vim .pydistutils.cfg
```

> .pydistutils.cfg
```cfg
[install]
prefix=
```

```sh
pip install --target=. Alfred-Workflow
```

#### REF
```sh
curl http://{user}:{pwd}@{domain}/crumbIssuer/api/json
curl 'http://{user}:{pwd}@{domain}/job/{job}/buildWithParameters' --data 'Jenkins-Crumb={crumb}&branch={branch}}'
```
