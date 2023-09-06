pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo "Building.."
                sh('ls -la')
                sh('pwd')
                sh('''#!/bin/bash
                ./prepare_env.sh
                ./main.sh --builder
                ''')            
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