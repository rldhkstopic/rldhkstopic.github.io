// 포스트 에디터 기능

let githubClient = null;
let isPreviewMode = false;

// 에디터 초기화
document.addEventListener('DOMContentLoaded', () => {
  if (!window.githubClient) {
    console.error('GitHub client not initialized');
    return;
  }
  
  githubClient = window.githubClient;
  
  initializeEditor();
  initializeToolbar();
  initializeAutoSave();
  initializeFilenameGeneration();
});

// 에디터 초기화
function initializeEditor() {
  const contentTextarea = document.getElementById('post-content');
  const titleInput = document.getElementById('post-title');
  const categorySelect = document.getElementById('post-category');
  const dateInput = document.getElementById('post-date');
  
  // 현재 날짜/시간 기본값 설정
  if (dateInput && !dateInput.value) {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    dateInput.value = `${year}-${month}-${day}T${hours}:${minutes}`;
  }
  
  // 키보드 단축키
  contentTextarea.addEventListener('keydown', (e) => {
    // Ctrl+B: 굵게
    if (e.ctrlKey && e.key === 'b') {
      e.preventDefault();
      insertMarkdown('**', '**');
    }
    // Ctrl+I: 기울임
    if (e.ctrlKey && e.key === 'i') {
      e.preventDefault();
      insertMarkdown('*', '*');
    }
    // Ctrl+K: 링크
    if (e.ctrlKey && e.key === 'k') {
      e.preventDefault();
      insertLink();
    }
  });
  
  // 미리보기 버튼
  document.getElementById('preview-btn').addEventListener('click', togglePreview);
  
  // 저장 버튼
  document.getElementById('save-draft-btn').addEventListener('click', saveDraft);
  
  // 게시 버튼
  document.getElementById('publish-btn').addEventListener('click', publishPost);
}

// 툴바 초기화
function initializeToolbar() {
  const toolbarButtons = document.querySelectorAll('.toolbar-btn');
  
  toolbarButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const action = btn.dataset.action;
      handleToolbarAction(action);
    });
  });
}

// 툴바 액션 처리
function handleToolbarAction(action) {
  const textarea = document.getElementById('post-content');
  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  const selectedText = textarea.value.substring(start, end);
  
  switch (action) {
    case 'bold':
      insertMarkdown('**', '**', selectedText);
      break;
    case 'italic':
      insertMarkdown('*', '*', selectedText);
      break;
    case 'heading':
      insertMarkdown('### ', '', selectedText);
      break;
    case 'link':
      insertLink(selectedText);
      break;
    case 'code':
      insertMarkdown('```\n', '\n```', selectedText);
      break;
    case 'quote':
      insertMarkdown('> ', '', selectedText);
      break;
    case 'list':
      insertMarkdown('- ', '', selectedText);
      break;
    case 'image':
      insertImage();
      break;
  }
}

// 마크다운 삽입
function insertMarkdown(before, after, selectedText = '') {
  const textarea = document.getElementById('post-content');
  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  
  const text = selectedText || '텍스트';
  const newText = before + text + after;
  
  textarea.value = textarea.value.substring(0, start) + newText + textarea.value.substring(end);
  textarea.focus();
  textarea.setSelectionRange(start + before.length, start + before.length + text.length);
}

// 링크 삽입
function insertLink(selectedText = '') {
  const text = selectedText || '링크 텍스트';
  const url = prompt('URL을 입력하세요:', 'https://');
  if (url) {
    insertMarkdown(`[${text}](`, ')', text);
    const textarea = document.getElementById('post-content');
    const pos = textarea.selectionStart;
    textarea.value = textarea.value.substring(0, pos - 1) + url + textarea.value.substring(pos - 1);
    textarea.setSelectionRange(pos + url.length, pos + url.length);
  }
}

// 이미지 삽입
function insertImage() {
  const alt = prompt('이미지 설명:', '');
  if (alt === null) return;
  const url = prompt('이미지 URL:', 'https://');
  if (url) {
    insertMarkdown(`![${alt}](`, ')', alt);
    const textarea = document.getElementById('post-content');
    const pos = textarea.selectionStart;
    textarea.value = textarea.value.substring(0, pos - 1) + url + textarea.value.substring(pos - 1);
    textarea.setSelectionRange(pos + url.length, pos + url.length);
  }
}

// 미리보기 토글
function togglePreview() {
  const textarea = document.getElementById('post-content');
  const previewPanel = document.getElementById('preview-panel');
  const previewContent = document.getElementById('preview-content');
  const previewBtn = document.getElementById('preview-btn');
  
  isPreviewMode = !isPreviewMode;
  
  if (isPreviewMode) {
    // 마크다운을 HTML로 변환
    if (typeof marked !== 'undefined') {
      previewContent.innerHTML = marked.parse(textarea.value);
    } else {
      previewContent.textContent = 'Marked.js가 로드되지 않았습니다.';
    }
    textarea.style.display = 'none';
    previewPanel.style.display = 'block';
    previewBtn.textContent = '편집';
  } else {
    textarea.style.display = 'block';
    previewPanel.style.display = 'none';
    previewBtn.textContent = '미리보기';
  }
}

// 파일명 자동 생성
function initializeFilenameGeneration() {
  const titleInput = document.getElementById('post-title');
  const filenameInput = document.getElementById('post-filename');
  const dateInput = document.getElementById('post-date');
  
  function updateFilename() {
    const title = titleInput.value.trim();
    const date = dateInput.value ? new Date(dateInput.value) : new Date();
    const dateStr = date.toISOString().split('T')[0];
    
    if (title) {
      const titleSlug = title
        .replace(/[^\w\s가-힣-]/g, '')
        .replace(/\s+/g, '-')
        .replace(/-+/g, '-')
        .toLowerCase();
      filenameInput.value = `${dateStr}-${titleSlug}.md`;
    } else {
      filenameInput.value = '';
    }
  }
  
  titleInput.addEventListener('input', updateFilename);
  dateInput.addEventListener('change', updateFilename);
}

// Front Matter 생성
function generateFrontMatter() {
  const title = document.getElementById('post-title').value.trim();
  const category = document.getElementById('post-category').value;
  const subcategory = document.getElementById('post-subcategory').value.trim();
  const tagsInput = document.getElementById('post-tags').value.trim();
  const dateInput = document.getElementById('post-date').value;
  
  if (!title || !category) {
    throw new Error('제목과 카테고리는 필수입니다.');
  }
  
  const date = dateInput ? new Date(dateInput) : new Date();
  const dateStr = date.toISOString().split('T')[0];
  const timeStr = date.toTimeString().split(' ')[0];
  
  const tags = tagsInput
    ? tagsInput.split(',').map(t => t.trim()).filter(t => t)
    : [];
  
  let frontMatter = `---
layout: post
title: "${title.replace(/"/g, '\\"')}"
date: ${dateStr} ${timeStr} +0900
author: rldhkstopic
category: ${category}`;
  
  if (subcategory) {
    frontMatter += `\nsubcategory: "${subcategory.replace(/"/g, '\\"')}"`;
  }
  
  if (tags.length > 0) {
    frontMatter += `\ntags: [${tags.map(t => `"${t}"`).join(', ')}]`;
  }
  
  frontMatter += `\nviews: 0
---

`;
  
  return frontMatter;
}

// 전체 마크다운 생성
function generateMarkdown() {
  const frontMatter = generateFrontMatter();
  const content = document.getElementById('post-content').value;
  return frontMatter + content;
}

// 임시 저장
async function saveDraft() {
  try {
    const markdown = generateMarkdown();
    const filename = document.getElementById('post-filename').value;
    
    if (!filename) {
      showStatus('파일명을 생성할 수 없습니다. 제목을 입력하세요.', 'error');
      return;
    }
    
    // 로컬스토리지에 임시 저장
    localStorage.setItem(`draft_${filename}`, markdown);
    localStorage.setItem(`draft_${filename}_meta`, JSON.stringify({
      title: document.getElementById('post-title').value,
      category: document.getElementById('post-category').value,
      date: new Date().toISOString()
    }));
    
    showStatus('임시 저장되었습니다.', 'success');
  } catch (error) {
    showStatus(`임시 저장 실패: ${error.message}`, 'error');
  }
}

// 게시
async function publishPost() {
  try {
    const markdown = generateMarkdown();
    const filename = document.getElementById('post-filename').value;
    const title = document.getElementById('post-title').value.trim();
    
    if (!filename || !title) {
      showStatus('제목과 파일명을 확인하세요.', 'error');
      return;
    }
    
    const path = `${window.ADMIN_CONFIG.postsPath}/${filename}`;
    
    // 파일 존재 여부 확인
    const fileInfo = await githubClient.getFileInfo(path);
    const sha = fileInfo ? fileInfo.sha : null;
    
    // 게시 확인
    const action = sha ? '업데이트' : '생성';
    if (!confirm(`포스트를 ${action}하시겠습니까?`)) {
      return;
    }
    
    showStatus('게시 중...', 'info');
    
    // GitHub에 파일 생성/업데이트
    const result = await githubClient.createOrUpdateFile(
      path,
      markdown,
      `Auto-post: ${title}`,
      sha
    );
    
    // 임시 저장 삭제
    localStorage.removeItem(`draft_${filename}`);
    localStorage.removeItem(`draft_${filename}_meta`);
    
    showStatus(`게시 완료! ${action}되었습니다.`, 'success');
    
    // 잠시 후 블로그 페이지로 이동
    setTimeout(() => {
      window.location.href = '/blog/';
    }, 2000);
    
  } catch (error) {
    showStatus(`게시 실패: ${error.message}`, 'error');
    console.error('Publish error:', error);
  }
}

// 상태 메시지 표시
function showStatus(message, type = 'info') {
  const statusDiv = document.getElementById('editor-status');
  statusDiv.textContent = message;
  statusDiv.className = `editor-status editor-status-${type}`;
  statusDiv.style.display = 'block';
  
  if (type === 'success' || type === 'error') {
    setTimeout(() => {
      statusDiv.style.display = 'none';
    }, 5000);
  }
}

// 자동 저장 (선택사항)
function initializeAutoSave() {
  const textarea = document.getElementById('post-content');
  let autoSaveTimer;
  
  textarea.addEventListener('input', () => {
    clearTimeout(autoSaveTimer);
    autoSaveTimer = setTimeout(() => {
      // 30초마다 자동 저장 (선택사항)
      // saveDraft();
    }, 30000);
  });
}


