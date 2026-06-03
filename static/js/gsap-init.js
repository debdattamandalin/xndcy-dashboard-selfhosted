// Central GSAP Animation Logic

document.addEventListener('DOMContentLoaded', () => {
    initPageAnimations();
    initSidebarHoverEffects();
});

// HTMX Hooks for Page Transitions
document.body.addEventListener('htmx:beforeSwap', function(evt) {
    // If the swap is a full page transition (e.g. hx-boost), we can intercept it
    // But hx-boost replaces the body by default. Let's just animate the main content out.
    // However, htmx swap happens synchronously if we don't delay it.
    // To properly delay HTMX swap, we can use a custom event or just let the new page animate IN instead.
    // A simple fade out doesn't block swap unless we prevent default. Let's just focus on animating IN.
});

document.body.addEventListener('htmx:afterSettle', function(evt) {
    // Re-initialize animations after an HTMX swap
    initPageAnimations();
});

function initPageAnimations() {
    // 1. Page Entrance Fade Up (Main Content Area)
    const mainContent = document.querySelector('main > *:not(header)');
    if (mainContent) {
        gsap.fromTo(mainContent, 
            { opacity: 0, y: 15 }, 
            { opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }
        );
    }

    // 2. Staggered Elements (.gsap-stagger)
    const staggerContainers = document.querySelectorAll('.gsap-stagger-container');
    
    // If there are specific containers, stagger their children. 
    // Otherwise, find all standalone stagger items.
    if (staggerContainers.length > 0) {
        staggerContainers.forEach(container => {
            const items = container.querySelectorAll('.gsap-stagger-item');
            if (items.length > 0) {
                gsap.fromTo(items, 
                    { opacity: 0, y: 20 },
                    { opacity: 1, y: 0, duration: 0.4, stagger: 0.05, ease: "power2.out", delay: 0.1 }
                );
            }
        });
    } else {
        const standaloneItems = document.querySelectorAll('.gsap-stagger-item');
        if (standaloneItems.length > 0) {
            gsap.fromTo(standaloneItems, 
                { opacity: 0, y: 20 },
                { opacity: 1, y: 0, duration: 0.4, stagger: 0.05, ease: "power2.out", delay: 0.1 }
            );
        }
    }
}

function initSidebarHoverEffects() {
    const navLinks = document.querySelectorAll('aside nav a');
    navLinks.forEach(link => {
        link.addEventListener('mouseenter', () => {
            if (!link.classList.contains('bg-[#448aff]')) {
                gsap.to(link, { x: 4, duration: 0.2, ease: "power1.out" });
            }
        });
        link.addEventListener('mouseleave', () => {
            if (!link.classList.contains('bg-[#448aff]')) {
                gsap.to(link, { x: 0, duration: 0.2, ease: "power1.out" });
            }
        });
    });
}

// Global helper for expanding details rows
window.animateRowExpand = function(rowId) {
    const row = document.getElementById(rowId);
    if (!row) return;
    
    // Close others
    document.querySelectorAll('.activity-details:not(.hidden)').forEach(el => {
        if (el.id !== rowId) {
            const content = el.querySelector('td > div');
            if (content) {
                gsap.to(content, {
                    opacity: 0, height: 0, y: -10, duration: 0.2, ease: "power2.in",
                    onComplete: () => {
                        el.classList.add('hidden');
                        gsap.set(content, { clearProps: "all" });
                    }
                });
            } else {
                el.classList.add('hidden');
            }
        }
    });

    if (row.classList.contains('hidden')) {
        // Expand
        row.classList.remove('hidden');
        const content = row.querySelector('td > div');
        if (content) {
            gsap.fromTo(content, 
                { opacity: 0, height: 0, y: -10 },
                { opacity: 1, height: 'auto', y: 0, duration: 0.3, ease: "power2.out" }
            );
        }
    } else {
        // Collapse
        const content = row.querySelector('td > div');
        if (content) {
            gsap.to(content, {
                opacity: 0, height: 0, y: -10, duration: 0.2, ease: "power2.in",
                onComplete: () => {
                    row.classList.add('hidden');
                    // Reset inline styles left by gsap so it doesn't break next time
                    gsap.set(content, { clearProps: "all" });
                }
            });
        } else {
            row.classList.add('hidden');
        }
    }
};
