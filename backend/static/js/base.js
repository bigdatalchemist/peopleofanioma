// Mobile menu toggle functionality
  const menuButton = document.getElementById('mobile-menu-button');
  const closeButton = document.getElementById('mobile-menu-close');
  const mobileMenu = document.getElementById('mobile-menu');
  const mobileMenuOverlay = document.getElementById('mobile-menu-overlay');
  const body = document.body;

  function openMobileMenu() {
    mobileMenu.classList.remove('hidden');
    mobileMenuOverlay.classList.remove('hidden');
    mobileMenu.classList.remove('-translate-x-full');
    body.classList.add('overflow-hidden');
  }

  function closeMobileMenu() {
    mobileMenu.classList.add('-translate-x-full');
    mobileMenuOverlay.classList.add('hidden');
    body.classList.remove('overflow-hidden');
    setTimeout(() => {
      mobileMenu.classList.add('hidden');
    }, 300);
  }

  menuButton.addEventListener('click', openMobileMenu);
  closeButton.addEventListener('click', closeMobileMenu);
  mobileMenuOverlay.addEventListener('click', closeMobileMenu);

  // Close on nav link click
  document.querySelectorAll('#mobile-menu a').forEach(link => {
    link.addEventListener('click', closeMobileMenu);
  });


    // Intersection Observer for fade-in sections
    const fadeSections = document.querySelectorAll('.fade-in-section');
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('fade-in');
          entry.target.classList.remove('opacity-0');
        }
      });
    }, { threshold: 0.1 });

    fadeSections.forEach(section => {
      observer.observe(section);
    });

    // Dark/Light Mode Toggle Functionality
    const themeToggle = document.getElementById('theme-toggle');
    const themeToggleDarkIcon = document.getElementById('theme-toggle-dark-icon');
    const themeToggleLightIcon = document.getElementById('theme-toggle-light-icon');

    // Check for saved user preference or use system preference
    if (localStorage.getItem('color-theme') === 'dark' || 
        (!localStorage.getItem('color-theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.classList.add('dark');
      themeToggleLightIcon.classList.remove('hidden');
    } else {
      document.documentElement.classList.remove('dark');
      themeToggleDarkIcon.classList.remove('hidden');
    }

    // Toggle button click handler
    themeToggle.addEventListener('click', function() {
      // Toggle icons
      themeToggleDarkIcon.classList.toggle('hidden');
      themeToggleLightIcon.classList.toggle('hidden');
      
      // Toggle theme
      if (document.documentElement.classList.contains('dark')) {
        document.documentElement.classList.remove('dark');
        localStorage.setItem('color-theme', 'light');
      } else {
        document.documentElement.classList.add('dark');
        localStorage.setItem('color-theme', 'dark');
      }
    });