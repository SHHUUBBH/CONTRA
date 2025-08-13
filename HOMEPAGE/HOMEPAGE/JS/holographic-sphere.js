document.addEventListener("DOMContentLoaded", function() {
  // Make all GIFs visible immediately
  const gifs = [
    document.getElementById("gif"),
    document.getElementById("gif2"),
    document.getElementById("gif3")
  ];
  
  // Apply to all GIFs
  gifs.forEach(gif => {
    if (gif) {
      gif.style.display = "block";
      gif.style.opacity = "1";
      gif.style.visibility = "visible";
    }
  });
});
