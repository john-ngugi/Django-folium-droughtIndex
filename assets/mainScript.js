   // Define an array of loading messages
   var loadingMessages = [
       'Loading data...',
       'Generating map...',
       'Adding layers...',
   ];

   // Get references to the loading overlay and message elements
   var loadingOverlay = document.getElementById('loading-overlay');
   var loadingMessage = document.getElementById('loading-message');

   // Show the loading overlay
   loadingOverlay.style.display = 'block';

   // Update the loading message every 2 seconds
   var messageIndex = 0;
   setInterval(function() {
       if (messageIndex < loadingMessages.length) {
           loadingMessage.textContent = loadingMessages[messageIndex];
           messageIndex++;
       }
   }, 2000);

   // Hide the loading overlay when the page has finished loading
   window.addEventListener('load', function() {
       loadingOverlay.style.display = 'none';
       document.getElementById('loading-overlay').classList.add('loaded');

   });

   function showLoadingScreen() {
       var loadingMessage = document.getElementById('processing-message');
       var processingMessages = [
           'Processing...',
           'This is taking longer than usual.\nplease wait...',
           'Motivating the catographers...',
           'Processing...'
       ];

       // Display the loading screen
       document.getElementById("loadingScreen").style.display = "block";

       var messageIndex = 0;
       setInterval(function() {
           if (messageIndex < processingMessages.length) {
               loadingMessage.textContent = processingMessages[messageIndex];
               messageIndex++;
           } else {
               // Reset the message index if it exceeds the array length
               messageIndex = 0;
           }
       }, 30000);
   }

   var toggleBtn = document.getElementById('toggle-side-menu');
   var next = document.getElementById('next')
   var closeSideMenu = document.getElementById('close-side-menu')

   toggleBtn.addEventListener('click', e => {
       next.classList.add('open');
   });

   closeSideMenu.addEventListener('click', e => {
       next.classList.remove('open');
   });