(function () {
  const form = document.querySelector('[data-avatar-form]');
  if (!form) return;

  const fileInput = form.querySelector('input[type="file"][name="photo"]');
  const cropperWrap = form.querySelector('[data-cropper-wrap]');
  const cropperImage = form.querySelector('[data-cropper-image]');
  const hiddenInput = form.querySelector('[data-cropped-photo]');

  if (!fileInput || !cropperWrap || !cropperImage || !hiddenInput || typeof window.Cropper === 'undefined') {
    return;
  }

  let cropper = null;

  fileInput.addEventListener('change', function (event) {
    const file = event.target.files && event.target.files[0];
    if (!file || !file.type.startsWith('image/')) {
      hiddenInput.value = '';
      return;
    }

    const reader = new FileReader();
    reader.onload = function (loadEvent) {
      cropperWrap.hidden = false;
      cropperImage.src = loadEvent.target.result;

      if (cropper) {
        cropper.destroy();
      }

      cropper = new window.Cropper(cropperImage, {
        aspectRatio: 1,
        viewMode: 1,
        autoCropArea: 1,
        responsive: true,
        dragMode: 'move',
        background: false,
        zoomable: true,
      });
    };
    reader.readAsDataURL(file);
  });

  form.addEventListener('submit', function () {
    if (!cropper || fileInput.files.length === 0) {
      hiddenInput.value = '';
      return;
    }

    const canvas = cropper.getCroppedCanvas({
      width: 512,
      height: 512,
      imageSmoothingQuality: 'high',
    });

    if (!canvas) {
      hiddenInput.value = '';
      return;
    }

    hiddenInput.value = canvas.toDataURL('image/jpeg', 0.92);
  });
})();
