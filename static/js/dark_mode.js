// Dark Mode Toggle with System Preference Detection
document.addEventListener('DOMContentLoaded', function() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const html = document.documentElement;
    
    // Function to set theme
    function setTheme(theme) {
        if (theme === 'dark') {
            html.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        } else {
            html.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        }
    }
    
    // Check for saved preference, otherwise check system preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        setTheme(savedTheme);
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        setTheme('dark');
    }
    
    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
            setTheme(e.matches ? 'dark' : 'light');
        }
    });
    
    // Toggle dark mode on button click
    darkModeToggle?.addEventListener('click', function() {
        const currentTheme = html.classList.contains('dark') ? 'dark' : 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    });
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href === '#') return;
        
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
            const offset = 80; // Account for fixed header
            const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - offset;
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// Lazy load images with Intersection Observer
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            }
        });
    }, {
        rootMargin: '50px'
    });

    document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
    });
}

// Enhanced scroll-to-top button
const createScrollTopButton = () => {
    const button = document.createElement('button');
    button.innerHTML = '<i class="fas fa-arrow-up"></i>';
    button.className = 'fixed bottom-6 right-6 w-12 h-12 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition-all opacity-0 pointer-events-none z-50';
    button.setAttribute('aria-label', 'Scroll to top');
    document.body.appendChild(button);

    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            button.classList.remove('opacity-0', 'pointer-events-none');
        } else {
            button.classList.add('opacity-0', 'pointer-events-none');
        }
    });

    button.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
};

// Initialize scroll-to-top button
createScrollTopButton();

// Reading progress bar
const createReadingProgress = () => {
    const article = document.querySelector('article');
    if (!article) return;

    const progressBar = document.createElement('div');
    progressBar.className = 'fixed top-0 left-0 h-1 bg-blue-600 z-50 transition-all duration-150';
    progressBar.style.width = '0%';
    document.body.appendChild(progressBar);

    window.addEventListener('scroll', () => {
        const articleTop = article.offsetTop;
        const articleHeight = article.offsetHeight;
        const windowHeight = window.innerHeight;
        const scrollPosition = window.pageYOffset;

        const scrollStart = articleTop;
        const scrollEnd = articleTop + articleHeight - windowHeight;
        const scrollDistance = scrollEnd - scrollStart;

        if (scrollPosition < scrollStart) {
            progressBar.style.width = '0%';
        } else if (scrollPosition > scrollEnd) {
            progressBar.style.width = '100%';
        } else {
            const progress = ((scrollPosition - scrollStart) / scrollDistance) * 100;
            progressBar.style.width = `${progress}%`;
        }
    });
};

// Initialize reading progress on article pages
if (document.querySelector('article')) {
    createReadingProgress();
}

// Copy code blocks functionality
document.querySelectorAll('pre code').forEach(block => {
    const button = document.createElement('button');
    button.innerHTML = '<i class="fas fa-copy"></i>';
    button.className = 'absolute top-2 right-2 px-3 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded text-sm transition';
    button.title = 'Copy code';
    
    const pre = block.parentElement;
    pre.style.position = 'relative';
    pre.appendChild(button);
    
    button.addEventListener('click', () => {
        navigator.clipboard.writeText(block.textContent).then(() => {
            button.innerHTML = '<i class="fas fa-check"></i> Copied!';
            setTimeout(() => {
                button.innerHTML = '<i class="fas fa-copy"></i>';
            }, 2000);
        });
    });
});

// Table of contents generator for long articles
const generateTableOfContents = () => {
    const article = document.querySelector('article .prose');
    if (!article) return;

    const headings = article.querySelectorAll('h2, h3');
    if (headings.length < 3) return; // Only create TOC if there are enough headings

    const toc = document.createElement('nav');
    toc.className = 'sticky top-24 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 mb-8';
    toc.innerHTML = '<h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">Table of Contents</h3><ul class="space-y-2 text-sm"></ul>';
    
    const tocList = toc.querySelector('ul');
    
    headings.forEach((heading, index) => {
        const id = `heading-${index}`;
        heading.id = id;
        
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.href = `#${id}`;
        a.textContent = heading.textContent;
        a.className = 'text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition';
        
        if (heading.tagName === 'H3') {
            li.className = 'ml-4';
        }
        
        li.appendChild(a);
        tocList.appendChild(li);
    });
    
    article.insertBefore(toc, article.firstChild);
};

// Initialize TOC on article pages
if (document.querySelector('article .prose')) {
    generateTableOfContents();
}

// Enhanced form validation
document.querySelectorAll('form').forEach(form => {
    const inputs = form.querySelectorAll('input[required], textarea[required]');
    
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (!this.value.trim()) {
                this.classList.add('border-red-500');
            } else {
                this.classList.remove('border-red-500');
            }
        });
    });
});

// Performance: Debounce function for scroll/resize events
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Search functionality with debouncing
const searchInput = document.querySelector('#categorySearch, #searchInput');
if (searchInput) {
    const handleSearch = debounce(function(e) {
        const searchTerm = e.target.value.toLowerCase();
        console.log('Searching for:', searchTerm);
        // Search logic handled in template-specific JS
    }, 300);
    
    searchInput.addEventListener('input', handleSearch);
}

// Print functionality for articles
const addPrintButton = () => {
    const article = document.querySelector('article');
    if (!article) return;

    const printBtn = document.createElement('button');
    printBtn.innerHTML = '<i class="fas fa-print mr-2"></i>Print Article';
    printBtn.className = 'px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition';
    printBtn.onclick = () => window.print();
    
    // Insert print button near article title
    const articleHeader = article.querySelector('h1');
    if (articleHeader && articleHeader.parentElement) {
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'mt-4';
        buttonContainer.appendChild(printBtn);
        articleHeader.parentElement.appendChild(buttonContainer);
    }
};

// Initialize print button
addPrintButton();

console.log('ModernBlog JS initialized successfully');