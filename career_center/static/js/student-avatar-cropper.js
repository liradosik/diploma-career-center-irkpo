(function () {
  const form = document.querySelector('[data-avatar-form]');
  if (!form) return;
  const fileInput = form.querySelector('input[type="file"][name="photo"]');
  const hiddenInput = form.querySelector('[data-cropped-photo]');
  const previewImage = form.querySelector('.role-avatar-img, .student-avatar-img');
  const fallbackNode = form.querySelector('.role-avatar-fallback, .student-avatar-fallback');
  const modal = document.querySelector('[data-avatar-modal]');
  const cropperImage = modal ? modal.querySelector('[data-cropper-image]') : null;
  const applyBtn = modal ? modal.querySelector('[data-avatar-apply]') : null;
  const cancelButtons = modal ? modal.querySelectorAll('[data-avatar-modal-cancel]') : [];

  if (!fileInput || !hiddenInput) return;
  if (typeof window.Cropper === 'undefined' || !modal || !cropperImage || !applyBtn) return;

  let cropper = null;
  let currentObjectUrl = '';
  let appliedPreviewSrc = previewImage ? previewImage.src : '';

  function closeModal(resetFile) {
    modal.hidden = true;
    if (cropper) {
      cropper.destroy();
      cropper = null;
    }
    if (currentObjectUrl) {
      URL.revokeObjectURL(currentObjectUrl);
      currentObjectUrl = '';
    }
    if (resetFile) {
      fileInput.value = '';
      hiddenInput.value = '';
    }
  }

  fileInput.addEventListener('change', function (event) {
    const file = event.target.files && event.target.files[0];
    if (!file || !file.type.startsWith('image/')) {
      hiddenInput.value = '';
      return;
    }
    hiddenInput.value = '';
    currentObjectUrl = URL.createObjectURL(file);
    cropperImage.src = currentObjectUrl;
    modal.hidden = false;
    cropper = new window.Cropper(cropperImage, {
      aspectRatio: 1,
      viewMode: 1,
      autoCropArea: 1,
      responsive: true,
      dragMode: 'move',
      background: false,
      zoomable: true,
    });
  });

  applyBtn.addEventListener('click', function () {
    if (!cropper) return;
    const canvas = cropper.getCroppedCanvas({
      width: 512,
      height: 512,
      imageSmoothingQuality: 'high',
    });
    if (!canvas) return;
    const dataUrl = canvas.toDataURL('image/jpeg', 0.92);
    hiddenInput.value = dataUrl;
    if (previewImage) {
      previewImage.src = dataUrl;
      appliedPreviewSrc = dataUrl;
    }
    if (fallbackNode) fallbackNode.style.display = 'none';
    closeModal(false);
  });

  cancelButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      if (previewImage && appliedPreviewSrc) previewImage.src = appliedPreviewSrc;
      closeModal(true);
    });
  });
})();
