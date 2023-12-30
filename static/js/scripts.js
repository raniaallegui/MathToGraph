
document.addEventListener("DOMContentLoaded", function () {
  const imageUploads = document.querySelectorAll(".image-upload");
  const images = document.querySelectorAll(".image");
  const addTextZoneButton = document.getElementById("add-text-zone");
  let currentElement = null;
  let dragX = 0;
  let dragY = 0;

  function handleMouseDown(e) {
    currentElement = e.target;
    dragX = e.offsetX;
    dragY = e.offsetY;
    e.stopPropagation();
  }

  function handleMouseUp() {
    currentElement = null;
  }

  function handleMouseMove(e) {
    if (currentElement) {
      // Use requestAnimationFrame for smoother animation
      requestAnimationFrame(function () {
        currentElement.style.transform = `translate(${e.clientX - dragX}px, ${e.clientY - dragY}px)`;
      });
    }
  }
  
  

  function addTextZone() {
    const newZone = document.createElement("div");
    newZone.classList.add("text-zone");
    newZone.contentEditable = true;
    newZone.style.left = "0";
    newZone.style.top = "0";
    document.body.appendChild(newZone);
    currentElement = newZone;
    newZone.addEventListener("mousedown", handleMouseDown);
    newZone.addEventListener("mouseup", handleMouseUp);
  }

  images.forEach(function (image) {
    image.addEventListener("mousedown", handleMouseDown);
    image.addEventListener("mouseup", handleMouseUp);
  });

  document.addEventListener("mousemove", handleMouseMove);

  imageUploads.forEach(function (imageUpload) {
    imageUpload.addEventListener("change", function (e) {
      const file = e.target.files[0];
      if (!file.type.match("image.*")) {
        alert("Le fichier sélectionné n'est pas une image.");
        return;
      }
      const reader = new FileReader();
      reader.onload = function (e) {
        const newImage = document.createElement("img");
        newImage.classList.add("image");
        newImage.src = e.target.result;
        newImage.width = "300";
        newImage.height = "200";
        newImage.addEventListener("mousedown", handleMouseDown);
        newImage.addEventListener("mouseup", handleMouseUp);
        document.body.appendChild(newImage);
      };
      reader.readAsDataURL(file);
    });
  });

  addTextZoneButton.addEventListener("click", addTextZone);
});