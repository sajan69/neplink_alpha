document.addEventListener('DOMContentLoaded', function() {
    const visibilitySelect = document.getElementById('visibility-{{ post.id }}');
    const selectedFriendsContainer = document.getElementById('selectedFriendsContainer-{{ post.id }}');
    const fileInput = document.getElementById('files-{{ post.id }}');
    const filePreview = document.getElementById('filePreview-{{ post.id }}');
    const maxFiles = 5;
    console.log(visibilitySelect);
    visibilitySelect.addEventListener('change', function() {
        if (this.value === 'selected') {
            selectedFriendsContainer.style.display = 'block';
        } else {
            selectedFriendsContainer.style.display = 'none';
        }
    });

    fileInput.addEventListener('change', function() {
        if (this.files.length > maxFiles) {
            alert(`You can only upload a maximum of ${maxFiles} files.`);
            this.value = '';
            return;
        }
        
        for (let i = 0; i < this.files.length; i++) {
            const file = this.files[i];
            const reader = new FileReader();	
            const previewItem = document.createElement('div');
            previewItem.className = 'preview-item mb-2';

            reader.onload = function(e) {
                if (file.type.startsWith('image/')) {
                    previewItem.innerHTML = `
                        <img src="${e.target.result}" alt="Preview" style="max-width: 100px; max-height: 100px;">
                        <span>${file.name}</span>
                        <button type="button" class="btn btn-sm btn-danger remove-file">Remove</button>
                    `;
                } else if (file.type.startsWith('video/')) {
                    previewItem.innerHTML = `
                        <video src="${e.target.result}" style="max-width: 100px; max-height: 100px;"></video>
                        <span>${file.name}</span>
                        <button type="button" class="btn btn-sm btn-danger remove-file">Remove</button>
                    `;
                } else {
                    previewItem.innerHTML = `
                        <i class="fas fa-file"></i>
                        <span>${file.name}</span>
                        <button type="button" class="btn btn-sm btn-danger remove-file">Remove</button>
                    `;
                }
            }
            reader.readAsDataURL(file);
            filePreview.appendChild(previewItem);
        }
    });

    filePreview.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-file')) {
            const mediaId = e.target.dataset.mediaId;
            if (mediaId) {
                const deletedMediaInput = document.createElement('input');
                deletedMediaInput.type = 'hidden';
                deletedMediaInput.name = 'deleted_media';
                deletedMediaInput.value = mediaId;
                e.target.closest('form').appendChild(deletedMediaInput);
            }
            e.target.closest('.preview-item').remove();
        }
    });

    const shareVisibilitySelect = document.getElementById('share-visibility-{{ post.id }}');
    const shareSelectedFriendsContainer = document.getElementById('shareSelectedFriendsContainer-{{ post.id }}');

    shareVisibilitySelect.addEventListener('change', function() {
        if (this.value === 'selected') {
            shareSelectedFriendsContainer.style.display = 'block';
        } else {
            shareSelectedFriendsContainer.style.display = 'none';
        }
    });
});

function toggleReplyForm(commentId) {
    const replyForm = document.getElementById(`reply-form-${commentId}`);
    replyForm.style.display = replyForm.style.display === 'none' ? 'block' : 'none';
}

document.addEventListener('DOMContentLoaded', function() {
   const carousels = document.querySelectorAll('.custom-carousel');

   carousels.forEach(carousel => {
       const items = carousel.querySelectorAll('.carousel-item');
       const indicators = carousel.querySelectorAll('.indicator');
       const prevButton = carousel.querySelector('.prev');
       const nextButton = carousel.querySelector('.next');
       let currentIndex = 0;

       function showItem(index) {
           items.forEach(item => item.classList.remove('active'));
           indicators.forEach(indicator => indicator.classList.remove('active'));
           items[index].classList.add('active');
           indicators[index].classList.add('active');
       }

       function showNext() {
           currentIndex = (currentIndex + 1) % items.length;
           showItem(currentIndex);
       }

       function showPrev() {
           currentIndex = (currentIndex - 1 + items.length) % items.length;
           showItem(currentIndex);
       }

       if (prevButton) prevButton.addEventListener('click', showPrev);
       if (nextButton) nextButton.addEventListener('click', showNext);

       indicators.forEach((indicator, index) => {
           indicator.addEventListener('click', () => {
               currentIndex = index;
               showItem(currentIndex);
           });
       });
   });
});