# Header Debug #1: Language Switching Bug

**Date:** 2025-10-13
**Status:** ✅ RESOLVED

## Problem Description

When switching languages in the header:
- **English (EN)**: Navigation menu items (Products, Portfolio, Blog, etc.) were completely invisible
- **Bahasa Indonesia (ID)**: Navigation displayed correctly
- **On refresh**: When refreshing in Bahasa, it would switch back to English (initially)

The navigation elements existed in the DOM with correct text content, but were visually hidden.

## Root Cause

**Global CSS Class Manipulation Conflict**

The website used two different language-switching approaches:

### 1. Header Approach (Text Replacement)
```javascript
productsText.textContent = translation; // "Products" → "Produk"
```
- Kept same elements visible
- Changed text content only
- Used `data-lang-en` and `data-lang-id` attributes on parent elements

### 2. Body Sections Approach (Show/Hide)
```javascript
const enElements = document.querySelectorAll('[data-lang-en]'); // Global selector!
enElements.forEach(el => el.classList.add('hidden')); // Hid ALL EN elements
```
- Used duplicate elements
- Toggled visibility with `hidden` class
- Used `data-lang-en="true"` and `data-lang-id="true"` attributes

### The Bug

Components like `Hero.astro`, `CTASection.astro`, and `EnterpriseSecurity.astro` were selecting **ALL elements on the entire page** with `data-lang-en` attribute:

```javascript
// BAD - Selects elements globally across entire page
const enElements = document.querySelectorAll('[data-lang-en]');
```

This included Header navigation elements like:
- `<button data-lang-en="Products">` (Products button)
- `<a data-lang-en="Portfolio">` (Portfolio link)
- `<a data-lang-en="Blog">` (Blog link)

When switching to Indonesian, these sections added `hidden` class to Header elements, making the entire navigation invisible!

## Solution

### Fixed All Body Sections to Use Scoped Selectors

Changed from **global** to **section-scoped** queries:

```javascript
// BEFORE (BAD):
function switchLanguage(lang) {
  const enElements = document.querySelectorAll('[data-lang-en]'); // Global!
  const idElements = document.querySelectorAll('[data-lang-id]');
  // ...
}

// AFTER (GOOD):
function switchLanguage(lang) {
  const section = document.querySelector('#hero-section'); // Get specific section
  if (!section) return;

  const enElements = section.querySelectorAll('[data-lang-en]'); // Scoped!
  const idElements = section.querySelectorAll('[data-lang-id]');
  // ...
}
```

### Files Modified

1. **Hero.astro** - Scoped to `#home` section
2. **CTASection.astro** - Added `#cta-section` ID, scoped queries
3. **EnterpriseSecurity.astro** - Added `#enterprise-security-section` ID, scoped queries
4. **GlobalStats.astro** - Already had proper scoping
5. **Header.astro** - Cleaned up and optimized language switching logic

### Additional Header Fixes

1. **Re-enabled automatic language loading on page refresh**
   ```javascript
   document.addEventListener('DOMContentLoaded', () => {
     const savedLang = localStorage.getItem('language') || 'EN';
     requestAnimationFrame(() => {
       setLanguage(savedLang, true);
     });
   });
   ```

2. **Used `requestAnimationFrame` for smooth rendering**
   - Prevents flicker on page load
   - Ensures language applies in next paint frame

3. **Added helper function for flexible attribute lookup**
   ```javascript
   const getTranslation = (element, langKey) => {
     // Check element itself first, then parent
     let translation = element.getAttribute(`data-lang-${langKey}`);
     if (!translation && element.parentElement) {
       translation = element.parentElement.getAttribute(`data-lang-${langKey}`);
     }
     return translation;
   };
   ```

## Why It Took Long to Debug

1. **Elements existed in DOM** - Console showed correct text content
2. **No JavaScript errors** - Everything ran "successfully"
3. **CSS visibility issue** - Hard to trace where `hidden` class came from
4. **Cross-file interference** - Header code looked fine; bug was in body sections
5. **Two conflicting patterns** - Text replacement vs show/hide approach

## Lessons Learned

### 1. Always Scope DOM Queries
```javascript
// ❌ BAD: Global selector
document.querySelectorAll('[data-lang-en]')

// ✅ GOOD: Scoped selector
section.querySelectorAll('[data-lang-en]')
```

### 2. Be Consistent with Patterns
- Header: Text replacement approach
- Body sections: Show/hide approach
- Both can coexist IF properly scoped

### 3. Use Unique Attribute Values
Instead of:
- Header: `data-lang-en="Products"` (value is translation)
- Body: `data-lang-en="true"` (value is boolean)

Better approach would be consistent naming to avoid conflicts.

### 4. Debugging Steps for Similar Issues
1. Check browser console for JavaScript errors
2. Inspect element in DevTools to see actual computed styles
3. Check for unexpected CSS classes (like `hidden`)
4. Search codebase for where those classes are added
5. Look for global DOM queries that might affect other components

## Testing Checklist

- [x] English displays correctly on first load
- [x] Switch to Bahasa - header changes and stays visible
- [x] Refresh page in Bahasa - stays in Bahasa smoothly
- [x] Switch back to English - header displays correctly
- [x] All navigation items visible in both languages
- [x] Body sections switch language correctly
- [x] No console errors

## Result

✅ **FULLY RESOLVED** - Header navigation now displays correctly in both English and Bahasa Indonesia with smooth switching and proper persistence across page refreshes.
