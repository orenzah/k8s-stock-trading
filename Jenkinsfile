pipeline {
  agent {
    kubernetes {
      label 'dind'            
    }
  }
  stages {    
    stage('Run Docker Things') {
      steps {
        container('dind') {
          sh 'docker ps'
        }
      }
    }
  }
}