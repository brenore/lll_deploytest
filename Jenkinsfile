def stsassume(awsaccount, environment, sessionname) {

                env.awsaccount=awsaccount
                env.sessionname=sessionname
                env.environment=environment


                def prodaccounts = ["1234","12345"]

                if (awsaccount in prodaccounts) {
                    timeout(time: 15, unit: "MINUTES") {
                        input message: 'Configuration Management must approve deployment to ' + environment, 
                        ok: 'I have reviewed and approve',
                        parameters: [string(defaultValue: '', description: 'CHG#', name: 'CHANGE', trim: false)],
                        submitter: 'AD_GROUP',
                        submitterParameter: 'APPROVER'
                    }
                }

                sh label: 'role', script: '''aws sts assume-role --role-arn arn:aws:iam::${awsaccount}:role/JenkinsExecutionRole --role-session-name ${sessionname} > temp_role'''
                env.AWS_ACCESS_KEY_ID = sh (script : "cat temp_role | jq .Credentials.AccessKeyId | xargs", returnStdout: true).trim()
                env.AWS_SECRET_ACCESS_KEY = sh (script : "cat temp_role | jq .Credentials.SecretAccessKey | xargs", returnStdout: true).trim()
                env.AWS_SESSION_TOKEN = sh (script : "cat temp_role | jq .Credentials.SessionToken | xargs", returnStdout: true).trim()
                env.AWS_DEFAULT_REGION = "us-east-1"
                sh label: 'removecred', script: '''rm temp_role'''
}

pipeline {
    agent any

    options { buildDiscarder(logRotator(numToKeepStr: '10')) }

    parameters { choice(name: 'AWS_ENV', choices: ['DEV', 'QAT', 'UAT'], description: 'AWS Env to Deploy')
                 choice(name: 'ONPREM_ENV', choices: ['DEV', 'QAT', 'UAT'], description: 'On-Prem Env to Point')
                 string(name: 'ENABLE_FEATURE_DEPLOY', defaultValue: "false", description: 'Enable creation for new environment for this feature')
                 string(name: 'FEATURE_AWS_ENV', defaultValue: "", description: 'Name of the new environment for feature')
                
    }

    environment {
        MASTER_BRANCH = 'master'
        PROJECT_NAME = "mobile-infra"
        AWS_DEFAULT_REGION = "us-east-1"
        DEV_ACCOUNT_ID = "317787813693"
        QAT_ACCOUNT_ID = "1234"
        UAT_ACCOUNT_ID = "1234"
        PROD_ACCOUNT_ID = "1234"

    }
    
    triggers { 
        pollSCM 'H/5 * * * *' 
    } 
    stages {

        stage('AWS-Login') {
            steps {
                script {
                    if (params.AWS_ENV == "DEV") {
                        ASSUME_ACCOUNT_ID = env.DEV_ACCOUNT_ID
                    } else if (params.AWS_ENV == "QAT") {
                        ASSUME_ACCOUNT_ID = env.QAT_ACCOUNT_ID
                    } else if (params.AWS_ENV == "UAT") {
                        ASSUME_ACCOUNT_ID = env.UAT_ACCOUNT_ID
                    } else if (params.AWS_ENV == "PROD") {
                        ASSUME_ACCOUNT_ID = env.PROD_ACCOUNT_ID
                    } else {
                        println "No Account Mentioned"
                        System.exit(1)  
                    }
                    env.ASSUME_ACCOUNT_ID = ASSUME_ACCOUNT_ID
                    println "ASSUME_ACCOUNT_ID is set to " + ASSUME_ACCOUNT_ID
                }
                stsassume("${ASSUME_ACCOUNT_ID}","${params.FEATURE_AWS_ENV}","${PROJECT_NAME}")
                sh "aws sts get-caller-identity"
            }
        }

        stage('Python-VirtualEnv') {
            steps {
                sh """
                    echo ${SHELL}
                    [ -d venv ] && rm -rf venv
                    virtualenv --python=python3.6 venv
                    source venv/bin/activate
                    export PATH=${VIRTUAL_ENV}/bin:${PATH}
                    #pip install --upgrade pip
                    pip install -r requirements.txt
                """
            }
        }

        stage('Run-Python') {
            steps {
                sh '''python ./deploy.py'''
            }
        }

 /*       stage('Sam-Deploy-Ondemand') {
            when {
                allOf {
                expression { params.ENABLE_FEATURE_DEPLOY == 'true'}
                expression { params.FEATURE_AWS_ENV?.trim() }
                }
             }
            steps {
                sh '''./scripts/package_ci.sh ${params.FEATURE_AWS_ENV} ${params.ONPREM_ENV}'''
                sh '''./scripts/deploy_ci.sh ${params.FEATURE_AWS_ENV} ${params.ONPREM_ENV}'''
            }
        }

        stage('Sam-Deploy') {
            when { 
                allOf {
                branch MASTER_BRANCH
                expression { params.AWS_ENV == 'true'}
                expression { params.ENABLE_FEATURE_DEPLOY != 'true'}
                }
            }
            steps {
                sh '''./scripts/package_ci.sh ${params.AWS_ENV} ${params.ONPREM_ENV}'''
                sh '''./scripts/deploy_ci.sh ${params.AWS_ENV} ${params.ONPREM_ENV}'''
            }
        }
         */ 
    }
}