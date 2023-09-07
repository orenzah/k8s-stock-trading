pipeline {
    agent any
    stages {
        stage('Build') {
            steps {                
                echo "Building..."
                sh "bash -c 'uname -a && cat /etc/issue'"                
                sh "bash -c 'sudo apt-get update && sudo apt-get install -y curl git'"
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