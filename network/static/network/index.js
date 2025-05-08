document.addEventListener('DOMContentLoaded', function() {
    // Give every single 'edit' anchor the ability to open up the edit field and hide the post
    document.querySelectorAll('.edit-anchor').forEach(item => {
        item.addEventListener('click', openEditField);
    });

    // Give every single like/unlike button an event listener to conduct like process
    document.querySelectorAll('.like-button').forEach(item => {
        item.addEventListener('click', likeActions);

        // Modify the inner html of the button to correlate with actual like status
        let isLiking = item.getAttribute('data-is-liking').toLowerCase() === 'true';
        item.textContent = isLiking ? 'Unlike' : 'Like';
    })
    
});

function openEditField(event) {
    event.preventDefault();
    // Get specific element's post id 
    const postId = event.target.getAttribute('data-post-id');

    // Get the 2 divs to hide and show.
    const postDiv = document.querySelector(`.main-post[data-post-id='${postId}']`);
    const editDiv = document.querySelector(`.edit-field[data-post-id='${postId}']`);

    // Hide and show the divs
    postDiv.style.display = 'none';
    editDiv.style.display = 'block';

    // Get the textarea and always prefill it with the content of the post
    const postContent = document.querySelector(`.post-content[data-post-id='${postId}']`).innerHTML;
    const editTextarea = document.querySelector(`.edit-content[data-post-id='${postId}']`);
    editTextarea.value = postContent;

    // Turn the save button on and off dynamically depending on whether textarea has content or not
    const submit = document.querySelector(`.edit-button[data-post-id='${postId}']`);
    submit.disabled = true; // Submit is disabled by default, awaiting a change

    // Add event listener to the form
    const form = document.querySelector(`.edit-form[data-post-id='${postId}']`);
    form.addEventListener('keyup', helper_submitKeyUp);

    // Add an event listener to the close and save button
    document.querySelector(`.close-button[data-post-id='${postId}']`).addEventListener('click', closeEditField);

    form.addEventListener('submit', saveEdit);
}

function closeEditField(event) {
    // Get specific element's post id 
    const postId = event.target.getAttribute('data-post-id');

    // Get the 2 divs to hide and show.
    const postDiv = document.querySelector(`.main-post[data-post-id='${postId}']`);
    const editDiv = document.querySelector(`.edit-field[data-post-id='${postId}']`);

    // Hide and show the divs
    postDiv.style.display = 'block';
    editDiv.style.display = 'none';

    // Remove event listener from the form that controls the submit button.
    const form = document.querySelector(`.edit-form[data-post-id='${postId}']`);
    form.removeEventListener('keyup', helper_submitKeyUp);

    // Remove event listener from the buttons
    document.querySelector(`.close-button[data-post-id='${postId}']`).removeEventListener('click', closeEditField);

    document.querySelector(`.edit-button[data-post-id='${postId}']`).removeEventListener('submit', saveEdit);   
}

function saveEdit(event) {
    event.preventDefault();
    // Get specific element's post id 
    const postId = event.target.getAttribute('data-post-id');

    // Get the content of the textarea on submission
    const postContent = document.querySelector(`.edit-content[data-post-id='${postId}']`).value;

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Send a PUT request to modify post in backend
    fetch(`/post_actions/${postId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            content: postContent
        })
    })

    // Send a GET request to get newly updated information
    .then(() => {
        return fetch(`/post_actions/${postId}`);
    })
    .then(response => response.json())

    // Modify HTML content of post
    .then(data => {
        document.querySelector(`.post-content[data-post-id='${postId}']`).innerHTML = data.content;
    })

    // Only close edit field after sending request
    .then(closeEditField(event));
    // Use .then() a lot, to load all the contents into the main page. Only THEN .then() use closeEditField there.
}

function likeActions(event) {
    // Get post ID as well as whether user already liked or not
    const postId = event.target.getAttribute('data-post-id');
    let isLiking = event.target.getAttribute('data-is-liking').toLowerCase() === 'true'; // Have to compare with true, because it'll be a string, not a bool

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Modify content
    fetch(`/post_actions/${postId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            like_status: !isLiking
        })
    })
    // Send a GET request to get newly updated information
    .then(() => {
        return fetch(`/post_actions/${postId}`);
    })
    .then(response => response.json())

    // Modify HTML content of the button as well as the like count
    .then(data => {
        document.querySelector(`.like-count[data-post-id='${postId}']`).innerHTML = `❤️ ${data.like_count}`;
    })
    // Asynchronously make the remaining changes to the HTML just to be on the safe side
    .then(() => {
        isLiking = !isLiking; // Change status

        document.querySelector(`.like-button[data-post-id='${postId}']`).setAttribute('data-is-liking', isLiking);
    })
    .then(() => {
        document.querySelector(`.like-button[data-post-id='${postId}']`).textContent = isLiking ? 'Unlike' : 'Like';
    })
}

function helper_submitKeyUp(event) {
    // Get specific element's post id 
    const postId = event.target.getAttribute('data-post-id');
    
    const submit = document.querySelector(`.edit-button[data-post-id='${postId}']`);

    const editTextarea = document.querySelector(`.edit-content[data-post-id='${postId}']`);

    if (editTextarea.value.length > 0) {
        submit.disabled = false;
    } else {
        submit.disabled = true;
    }
}