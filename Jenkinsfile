pipeline {
    agent any
    environment {
        IMAGE = "python-3.8-buster-project-packages"
        CONTAINER_NAME = "flask-project"
        
    }
    stages {
      
        stage('Build') {
            steps {
                //  Building new image
                sh '/usr/local/bin/docker image build -t $IMAGE:latest .'
         //       sh 'docker image tag $DOCKER_HUB_REPO:latest $DOCKER_HUB_REPO:$BUILD_NUMBER'

                //  Pushing Image to Repository
         //       sh 'docker push desynchd/docker101tutorial:$BUILD_NUMBER'
           //     sh 'docker push desynchd/docker101tutorial:latest'
                
                echo "Image built and pushed to repository"
            }
        }
        stage('Deploy') {
            steps {
                script{
    
                   sh '/usr/local/bin/docker stop $CONTAINER_NAME'
                   sh '/usr/local/bin/docker rm $CONTAINER_NAME'
                   sh '/usr/local/bin/docker run --name $CONTAINER_NAME -d -p 5000:5000 $IMAGE'
                        
                   sh 'echo "Latest image/code deployed"'
                }
            }
        }
    }
}
