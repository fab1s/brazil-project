// A module/network failure must leave an actionable message, not an endless spinner.
try {
  await import('./app.js?v=20261007-obras-screened');
} catch (error) {
  console.error('Map startup failed', error);
  document.querySelector('#mapLoadingText').textContent='Map could not start. Check your connection and retry.';
  const retry=document.querySelector('#retryMap');retry.hidden=false;
  retry.addEventListener('click',()=>location.reload());
}
