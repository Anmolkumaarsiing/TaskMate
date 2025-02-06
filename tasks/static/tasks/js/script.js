// ScrollReveal Configuration
ScrollReveal({
  mobile: false,
});

ScrollReveal().reveal('.header', {
  delay: 500,
  reset: false,
  mobile: false,
});



ScrollReveal().reveal('.section-title', {
  reset: true,
  duration: 1500,
  delay: 500,
  origin: 'left',
  distance: '50px',
});


ScrollReveal().reveal('.about-content', {
  reset: true,
  duration: 1500,
  origin: 'left',
  distance: '50px',
});

ScrollReveal().reveal('.about-img', {
  reset: true,
  duration: 1500,
  origin: 'right',
  distance: '50px',
});