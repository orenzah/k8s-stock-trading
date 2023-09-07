pipeline {
    agent any
    stages {
        stage('Build') {
            agent {
                docker {
                    image 'ubuntu'
                    args '-v /var/run:/var/run'
                }
            }
            steps {                
                echo "Building..."
                sh "bash -c 'uname -a && cat /etc/issue'"                
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