<template>
  <div class="doc-page">
    <div class="doc-container">
      
      <main class="doc-content">
        <router-view></router-view> 
      </main>

    </div>
  </div>
</template>

<style scoped>
/* --- LAYOUT --- */
.doc-page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #fcfcfc;
}

.doc-container {
  display: flex;
  justify-content: center; /* Centers the content block */
  max-width: 1000px; /* Controls the maximum width of your cards. Increase to 1200px if you want them wider */
  width: 100%;
  margin: 0 auto;
  padding: 40px 20px;
  flex: 1;
}

/* --- MAIN CONTENT CONTAINER --- */
.doc-content {
  flex-grow: 1;
  width: 100%; /* Ensures it fills the doc-container */
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .doc-container {
    padding: 20px 15px; /* Slightly tighter padding on mobile */
  }
}
</style>

/* --- SHARED DOCUMENTATION TYPOGRAPHY --- */
<style>
/* Target elements specifically inside the main content area */
.doc-content section {
  margin-bottom: 60px;
  scroll-margin-top: 100px; /* Ensures headers don't hide behind the navbar */
}

.doc-content h1 {
  font-size: 2.5rem;
  color: #0b1e3b;
  margin-bottom: 20px;
}

.doc-content h2 {
  font-size: 1.8rem;
  color: #0b1e3b;
  border-bottom: 1px solid #ddd;
  padding-bottom: 10px;
  margin-top: 0;
}

.doc-content h3 {
  font-size: 1.3rem;
  color: #444;
  margin-top: 25px;
}

.doc-content p, 
.doc-content li {
  line-height: 1.7;
  color: #444;
  font-size: 1.05rem;
}

.doc-content .intro-text {
  font-size: 1.2rem;
  color: #555;
  border-left: 4px solid #0056b3;
  padding-left: 20px;
}

/* Citation style */
.doc-content .citation-block {
  background: #f5f5f5;
  padding: 20px;
  font-family: 'Courier New', Courier, monospace;
  border-radius: 6px;
  border: 1px solid #ddd;
}
</style>