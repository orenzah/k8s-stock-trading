pipeline {
    agent any
    stages {
        stage('build') {
            steps {
                sh '. /.venv/bin/activate && python3 main.py --builder'                
            }            
        }
        stage('deploy') {
            steps {                
                sh '. /.venv/bin/activate && python3 main.py --deployer --ci-mode'
            }
        }
    }
}