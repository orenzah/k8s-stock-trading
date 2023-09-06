pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo "Building.."
                sh('ls -la')
                sh('pwd')
                sh('sh /var/jenkins_home/workspace/github/prepare.sh')            
            }
        }
        stage('Test') {
            steps {
                echo 'Testing..'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying....'
                sh "bash -c 'main.sh --deployer'"
            }
        }
    }
}