pipeline {
    agent any
    stages {
        stage('build') {
            steps {
                sh 'env -C ./stocks docker build --target base -t python-base . -f Dockerfile'
                sh 'env -C ./stocks docker build --target app -t python-app . -f Dockerfile'
                sh 'docker tag python-app cr.zahtlv.freeddns.org/python-app:latest'
                sh 'docker push cr.zahtlv.freeddns.org/python-app:latest'                
            }            
        }
        stage('deploy') {
            steps {                
                sh '. .venv/bin/activate && python3 main.py --deployer --ci-mode'
            }
        }
    }
}