pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo "Building.."
                sh "./prepare.sh"
                sh "./main.sh --builder --base"
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