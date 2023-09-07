pipeline {
    agent any
    stages {
        stage('Build') {
            steps {                
                echo "Building..."
                sh "bash -c 'uname -a && cat /etc/issue'"                
                sh "bash -c 'sudo docker build --target ci -t python-ci . -f ./ci/Dockerfile'"
                sh "bash -c 'sudo docker run --rm -v $(pwd):/app python-ci python3 main.py --builder --base'"
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