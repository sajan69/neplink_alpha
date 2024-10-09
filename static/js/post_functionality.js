function initializePostFunctionality(csrftoken, postManagementUrl) {
    function sendPostRequest(action, postId, additionalData = {}) {
        const data = {
            action: action,
            post_id: postId,
            ...additionalData
        };
        console.log("Sending data:", data);  // Debug log
        return fetch(postManagementUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        }).then(response => response.json());
    }

    function renderComment(comment, postId) {
        return `
            <div class="mb-2" id="comment-${comment.id}">
                <strong>${comment.user}</strong>: <span class="comment-text">${comment.text}</span>
                <small class="text-muted">${comment.created_at}</small>
                <button class="btn btn-outline-primary btn-sm like-button" data-type="comment" data-id="${comment.id}" data-post-id="${postId}">
                    ${comment.is_liked_by_user ? 'Unlike' : 'Like'} (${comment.likes_count})
                </button>
                ${comment.is_owner ? `
                    <button class="btn btn-outline-secondary btn-sm edit-comment-button" data-id="${comment.id}">Edit</button>
                    <button class="btn btn-outline-danger btn-sm delete-comment-button" data-id="${comment.id}">Delete</button>
                ` : ''}
                <button class="btn btn-outline-secondary btn-sm reply-button" data-id="${comment.id}">Reply</button>
                <div class="ms-3 mt-2" id="replies-${comment.id}">
                    ${comment.replies.map(reply => renderReply(reply, postId)).join('')}
                </div>
            </div>
        `;
    }

    function renderReply(reply, postId) {
        return `
            <div class="mb-1" id="reply-${reply.id}">
                <strong>${reply.user}</strong>: <span class="reply-text">${reply.text}</span>
                <small class="text-muted">${reply.created_at}</small>
                <button class="btn btn-outline-primary btn-sm like-button" data-type="reply" data-id="${reply.id}" data-post-id="${postId}">
                    ${reply.is_liked_by_user ? 'Unlike' : 'Like'} (${reply.likes_count})
                </button>
                ${reply.is_owner ? `
                    <button class="btn btn-outline-secondary btn-sm edit-reply-button" data-id="${reply.id}">Edit</button>
                    <button class="btn btn-outline-danger btn-sm delete-reply-button" data-id="${reply.id}">Delete</button>
                ` : ''}
            </div>
        `;
    }

    function attachEventListeners(postId) {
        const postElement = document.getElementById(`post-${postId}`);

        // Like functionality
        postElement.querySelectorAll('.like-button').forEach(button => {
            button.addEventListener('click', function() {
                const type = this.dataset.type;
                const id = this.dataset.id;
                sendPostRequest(`like_${type}`, postId, { id: id })
                    .then(data => {
                        if (data.status === 'success') {
                            this.textContent = `${data.action === 'liked' ? 'Unlike' : 'Like'} (${data.likes_count})`;
                            Swal.fire({
                                icon: 'success',
                                title: 'Success',
                                text: data.message,
                                timer: 1500,
                                showConfirmButton: false
                            });
                        }
                    });
            });
        });

        // Add comment
        postElement.querySelector('.comment-form').addEventListener('submit', function(e) {
            e.preventDefault();
            const text = this.elements.text.value;
            sendPostRequest('add_comment', postId, { text: text })
                .then(data => {
                    if (data.status === 'success') {
                        const commentsList = postElement.querySelector('#comments-list-' + postId);
                        commentsList.insertAdjacentHTML('afterbegin', renderComment(data, postId));
                        this.reset();
                        attachEventListeners(postId);
                    }
                });
        });

        // Edit comment
        postElement.querySelectorAll('.edit-comment-button').forEach(button => {
            button.addEventListener('click', function() {
                const commentId = this.dataset.id;
                const commentElement = document.getElementById(`comment-${commentId}`);
                const commentText = commentElement.querySelector('.comment-text').textContent;
                
                Swal.fire({
                    title: 'Edit Comment',
                    input: 'textarea',
                    inputValue: commentText,
                    showCancelButton: true,
                    confirmButtonText: 'Save',
                    cancelButtonText: 'Cancel',
                    preConfirm: (text) => {
                        if (!text.trim()) {
                            Swal.showValidationMessage('Comment cannot be empty');
                        }
                        return text;
                    }
                }).then((result) => {
                    if (result.isConfirmed) {
                        sendPostRequest('edit_comment', postId, { comment_id: commentId, text: result.value })
                            .then(data => {
                                if (data.status === 'success') {
                                    commentElement.querySelector('.comment-text').textContent = data.text;
                                    Swal.fire('Success', 'Comment updated successfully', 'success');
                                }
                            });
                    }
                });
            });
        });

        // Delete comment
        postElement.querySelectorAll('.delete-comment-button').forEach(button => {
            button.addEventListener('click', function() {
                const commentId = this.dataset.id;
                Swal.fire({
                    title: 'Are you sure?',
                    text: "You won't be able to revert this!",
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#d33',
                    cancelButtonColor: '#3085d6',
                    confirmButtonText: 'Yes, delete it!'
                }).then((result) => {
                    if (result.isConfirmed) {
                        sendPostRequest('delete_comment', postId, { comment_id: commentId })
                            .then(data => {
                                if (data.status === 'success') {
                                    document.getElementById(`comment-${commentId}`).remove();
                                    Swal.fire('Deleted!', 'Your comment has been deleted.', 'success');
                                }
                            });
                    }
                });
            });
        });

        // Add reply
        postElement.querySelectorAll('.reply-button').forEach(button => {
            button.addEventListener('click', function() {
                const commentId = this.dataset.id;
                Swal.fire({
                    title: 'Add Reply',
                    input: 'textarea',
                    inputPlaceholder: 'Write your reply here...',
                    showCancelButton: true,
                    confirmButtonText: 'Reply',
                    cancelButtonText: 'Cancel',
                    preConfirm: (text) => {
                        if (!text.trim()) {
                            Swal.showValidationMessage('Reply cannot be empty');
                        }
                        return text;
                    }
                }).then((result) => {
                    if (result.isConfirmed) {
                        sendPostRequest('add_reply', postId, { comment_id: commentId, text: result.value })
                            .then(data => {
                                if (data.status === 'success') {
                                    const repliesList = document.getElementById(`replies-${commentId}`);
                                    repliesList.insertAdjacentHTML('beforeend', renderReply(data, postId));
                                    attachEventListeners(postId);
                                    Swal.fire('Success', 'Reply added successfully', 'success');
                                }
                            });
                    }
                });
            });
        });

        // Edit reply
        postElement.querySelectorAll('.edit-reply-button').forEach(button => {
            button.addEventListener('click', function() {
                const replyId = this.dataset.id;
                const replyElement = document.getElementById(`reply-${replyId}`);
                const replyText = replyElement.querySelector('.reply-text').textContent;
                
                Swal.fire({
                    title: 'Edit Reply',
                    input: 'textarea',
                    inputValue: replyText,
                    showCancelButton: true,
                    confirmButtonText: 'Save',
                    cancelButtonText: 'Cancel',
                    preConfirm: (text) => {
                        if (!text.trim()) {
                            Swal.showValidationMessage('Reply cannot be empty');
                        }
                        return text;
                    }
                }).then((result) => {
                    if (result.isConfirmed) {
                        sendPostRequest('edit_reply', postId, { reply_id: replyId, text: result.value })
                            .then(data => {
                                if (data.status === 'success') {
                                    replyElement.querySelector('.reply-text').textContent = data.text;
                                    Swal.fire('Success', 'Reply updated successfully', 'success');
                                }
                            });
                    }
                });
            });
        });

        // Delete reply
        postElement.querySelectorAll('.delete-reply-button').forEach(button => {
            button.addEventListener('click', function() {
                const replyId = this.dataset.id;
                Swal.fire({
                    title: 'Are you sure?',
                    text: "You won't be able to revert this!",
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#d33',
                    cancelButtonColor: '#3085d6',
                    confirmButtonText: 'Yes, delete it!'
                }).then((result) => {
                    if (result.isConfirmed) {
                        sendPostRequest('delete_reply', postId, { reply_id: replyId })
                            .then(data => {
                                if (data.status === 'success') {
                                    document.getElementById(`reply-${replyId}`).remove();
                                    Swal.fire('Deleted!', 'Your reply has been deleted.', 'success');
                                }
                            });
                    }
                });
            });
        });

        // Edit post
        const editPostButton = postElement.querySelector('.edit-post-button');
        if (editPostButton) {
            editPostButton.addEventListener('click', function() {
                const postId = this.dataset.id;
                const postCaption = postElement.querySelector('.post-caption').textContent;
                const postFeeling = postElement.querySelector('.post-feeling') ? postElement.querySelector('.post-feeling').textContent.replace('Feeling ', '') : '';
                
                Swal.fire({
                    title: 'Edit Post',
                    html:
                        '<textarea id="swal-input1" class="swal2-textarea" placeholder="Caption">' + postCaption + '</textarea>' +
                        '<input id="swal-input2" class="swal2-input" placeholder="Feeling" value="' + postFeeling + '">' +
                        '<input id="swal-input3" type="file" class="swal2-file" accept="image/*,video/*,audio/*">',
                    focusConfirm: false,
                    preConfirm: () => {
                        const caption = document.getElementById('swal-input1').value;
                        const feeling = document.getElementById('swal-input2').value;
                        const mediaFile = document.getElementById('swal-input3').files[0];
                        
                        if (!caption.trim()) {
                            Swal.showValidationMessage('Caption cannot be empty');
                            return false;
                        }
                        
                        const formData = new FormData();
                        formData.append('action', 'edit_post');
                        formData.append('post_id', postId);
                        formData.append('caption', caption);
                        formData.append('feeling', feeling);
                        if (mediaFile) {
                            formData.append('media', mediaFile);
                        }
                        
                        return fetch(postManagementUrl, {
                            method: 'POST',
                            headers: {
                                'X-CSRFToken': csrftoken
                            },
                            body: formData
                        }).then(response => response.json());
                    }
                }).then((result) => {
                    if (result.isConfirmed && result.value.status === 'success') {
                        postElement.querySelector('.post-caption').textContent = result.value.caption;
                        const feelingElement = postElement.querySelector('.post-feeling');
                        if (result.value.feeling) {
                            if (feelingElement) {
                                feelingElement.textContent = 'Feeling ' + result.value.feeling;
                            } else {
                                postElement.querySelector('.card-body').insertAdjacentHTML('beforeend', `<p class="post-feeling"><i class="fas fa-smile"></i> Feeling ${result.value.feeling}</p>`);
                            }
                        } else if (feelingElement) {
                            feelingElement.remove();
                        }
                        if (result.value.media_url) {
                            const mediaElement = postElement.querySelector('.post-media');
                            if (mediaElement) {
                                mediaElement.innerHTML = `<img src="${result.value.media_url}" alt="Post image" class="img-fluid rounded">`;
                            } else {
                                postElement.querySelector('.card-body').insertAdjacentHTML('afterbegin', `<div class="post-media mb-3"><img src="${result.value.media_url}" alt="Post image" class="img-fluid rounded"></div>`);
                            }
                        }
                        Swal.fire('Success', 'Post updated successfully', 'success');
                    }
                });
            });
        }

        // Delete post
        const deletePostButton = postElement.querySelector('.delete-post-button');
        if (deletePostButton) {
            deletePostButton.addEventListener('click', function() {
                const postId = this.dataset.id;
                Swal.fire({
                    title: 'Are you sure?',
                    text: "You won't be able to revert this!",
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#d33',
                    cancelButtonColor: '#3085d6',
                    confirmButtonText: 'Yes, delete it!'
                }).then((result) => {
                    if (result.isConfirmed) {
                        sendPostRequest('delete_post', postId)
                            .then(data => {
                                if (data.status === 'success') {
                                    postElement.remove();
                                    Swal.fire('Deleted!', 'Your post has been deleted.', 'success');
                                    if (data.redirect_url) {
                                        window.location.href = data.redirect_url;
                                    }
                                }
                            });
                    }
                });
            });
        }

        // Comment filter functionality
        postElement.querySelectorAll('.comment-filter').forEach(filter => {
            filter.addEventListener('click', function(e) {
                e.preventDefault();
                const filterType = this.dataset.filter;
                sendPostRequest('get_comments', postId, { filter: filterType })
                    .then(data => {
                        if (data.status === 'success') {
                            const commentsList = postElement.querySelector('#comments-list-' + postId);
                            commentsList.innerHTML = data.comments.map(comment => renderComment(comment, postId)).join('');
                            attachEventListeners(postId);
                        }
                    });
            });
        });
    }

    // Initial attachment of event listeners
    document.querySelectorAll('.post').forEach(post => {
        const postId = post.id.replace('post-', '');
        attachEventListeners(postId);
    });
}