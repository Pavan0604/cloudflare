import { postToQueue } from "../mod/sqs"

addEventListener('fetch', event => {
    event.respondWith(handleRequest(event.request))
    })
    
     /**   
      // @param {Request} request
      */
async function handleRequest(request) {
     
    if (request.method == "POST") {
     let msg = "hello sqs!"
     let region = "ap-south-1"
     let queuePath = "/244455244329/test"
     let response = await sqs.postToQueue(region, msg, queuePath, tx6jGE0OJYNct5BdxutZN04qVoHcDTaB6Qg6z0mF, AKIAXMDNKYWNUHV6FRUT);
     return (response);
        }
    
      return new Response('Please use a POST method to send messages to SQS', {
        headers: { 'content-type': 'text/plain' },
        })
}
    
    
