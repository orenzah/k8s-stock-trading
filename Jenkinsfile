pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo "Building.."
                sh "ls -la"
                sh "bash -c 'main.sh --builder --base'"
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