document.querySelectorAll('#sidebar a.nav-link').forEach(link=>{if(link.pathname===location.pathname)link.classList.add('active');});
