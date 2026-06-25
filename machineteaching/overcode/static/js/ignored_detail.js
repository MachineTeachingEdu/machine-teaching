let activeUserId = null;
let studentsPerPage = 8;
let currentPage = 1;
let students = [];
let filtered = [];
let solutions = [];
let llm_state = {};
let currentSolutionIndex = null;

function escapeHtml(text){
    return (text || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

function normalizeMarkdown(text){
    return (text || "")
        .replace(/\r\n/g, "\n")
        .replace(/^[ \t]+(#{1,6}\s+)/gm, "$1")
        .replace(/^[ \t]+([-*]\s+)/gm, "$1");
}

function fallbackMarkdownToHtml(text){
    const lines = normalizeMarkdown(text).split("\n");
    let html = "";
    let inList = false;

    lines.forEach(function(line){
        const trimmed = line.trim();

        if(!trimmed){
            if(inList){
                html += "</ul>";
                inList = false;
            }
            return;
        }

        const heading = trimmed.match(/^(#{1,6})\s+(.+)$/);
        if(heading){
            if(inList){
                html += "</ul>";
                inList = false;
            }

            const level = Math.min(heading[1].length, 6);
            html += `<h${level}>${escapeHtml(heading[2])}</h${level}>`;
            return;
        }

        const bullet = trimmed.match(/^[-*]\s+(.+)$/);
        if(bullet){
            if(!inList){
                html += "<ul>";
                inList = true;
            }

            html += `<li>${escapeHtml(bullet[1])}</li>`;
            return;
        }

        if(inList){
            html += "</ul>";
            inList = false;
        }

        html += `<p>${escapeHtml(trimmed)}</p>`;
    });

    if(inList){
        html += "</ul>";
    }

    return html;
}

function markdownToHtml(text){
    const markdown = normalizeMarkdown(text);

    if (window.showdown) {
        const converter = new showdown.Converter({
            simplifiedAutoLink: true,
            simpleLineBreaks: true
        });

        return converter.makeHtml(escapeHtml(markdown));
    }

    return fallbackMarkdownToHtml(markdown);
}

function init(){
    students = [...document.querySelectorAll(".student")];
    solutions = [...document.querySelectorAll(".solution-detail")];
    filtered = [...students];
    renderSavedComments();
    showPage(1);
}

function renderSavedComments(){
    document
        .querySelectorAll(".comment-text-overcode")
        .forEach(function(comment){
            const markdown = comment.textContent;
            comment.innerHTML = markdownToHtml(markdown);
            comment.classList.add("llm-markdown-overcode");
        });
}

function hideAll(elements){
    elements.forEach(e => e.style.display="none");
}

function showPage(page){
    currentPage = page;
    hideAll(students);

    let start = (page-1) * studentsPerPage;
    let end = start + studentsPerPage;

    filtered.slice(start,end).forEach(el=>{
        el.style.display="block";
    });

    let total = Math.ceil(filtered.length/studentsPerPage);
    document.getElementById("page-info").innerText = page+" / "+total;
}

function nextPage(){
    let total=Math.ceil(filtered.length/studentsPerPage);
    if(currentPage<total) showPage(currentPage+1);
}

function prevPage(){
    if(currentPage>1) showPage(currentPage-1);
}

function searchStudent(){
    let value=document.getElementById("search").value.toLowerCase();
    filtered = students.filter(el => el.dataset.name.includes(value));
    showPage(1);
}

function showSolution(id){
    activeUserId = id;

    document.getElementById("student-section").style.display="none";
    hideAll(solutions);

    let element=document.getElementById("solution-"+id);
    element.style.display="block";

    currentSolutionIndex = [...solutions]
        .map(el => el.id)
        .indexOf("solution-" + id);

    // sincroniza URL SEM reload
    window.location.hash = "solution-" + id;
}

function nextSolution(){
    if(currentSolutionIndex < solutions.length-1){
        solutions[currentSolutionIndex].style.display="none";
        currentSolutionIndex++;
        solutions[currentSolutionIndex].style.display="block";
    }
}

function prevSolution(){
    if(currentSolutionIndex>0){
        solutions[currentSolutionIndex].style.display="none";
        currentSolutionIndex--;
        solutions[currentSolutionIndex].style.display="block";
    }
}

function backToStudents(){
    hideAll(solutions);
    document.getElementById("student-section").style.display="block";
}

window.onload = function() {
    init();
    let hash = window.location.hash;
    if(hash.startsWith("#solution-")){
        let id = hash.replace("#solution-", "");
        showSolution(id);
    }
};

function saveComment(userId){
    const textarea = document.getElementById("comment-" + userId);
    const content = textarea.value;

    fetch(window.overcodeConfig.commentUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: new URLSearchParams({
            user_id: userId,
            selected_user: userId,
            content: content
        })
    })
    .then(() => {
        reloadSolution(userId)
    });
}

function generateLLMForStudent(userId){
    const loadingEl = document.getElementById("llm-loading-" + userId);
    const outputEl = document.getElementById("llm-output-" + userId);

    if (loadingEl) loadingEl.style.display = "block";
    if (outputEl) outputEl.innerHTML = "";

    const solutionEl = document.getElementById("solution-" + userId);
    const code = solutionEl ? solutionEl.querySelector(".code-block-overcode pre")?.innerText || "" : "";

    fetch(window.overcodeConfig.llmGroupCommentUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({
            code: code,
            group_id: null,
            user_id: userId,
            ignored: true
        })
    })
    .then(async (res) => {
        const text = await res.text();
        let data;
        try { data = JSON.parse(text); }
        catch (e) { throw new Error("Resposta inválida do servidor: " + text); }

        if (!res.ok) throw new Error(data.error || "Erro na API");

        return data;
    })
    .then(data => {
        if (loadingEl) loadingEl.style.display = "none";

        const comment = data?.comment || "Sem resposta da IA";
        llm_state[userId] = { comment: comment, accepted: null };
        const commentHtml = markdownToHtml(comment);

        outputEl.innerHTML =
        `<div class="card llm-card-overcode">
            <p><strong>Comentário sugerido pela IA:</strong></p>
            <div class="llm-markdown-overcode">${commentHtml}</div>
            <div class="llm-actions-overcode">
                <button type="button" class="primary action-button-overcode" onclick="acceptLLM(${userId})">Usar comentário</button>
                <button type="button" class="secondary-button-overcode" onclick="rejectLLM(${userId})">Não usar</button>
            </div>
        </div>`;
    })
    .catch(err => {
        if (loadingEl) loadingEl.style.display = "none";
        outputEl.innerHTML =
        `<div class="card">
            <p>Erro: ${err.message}</p>
        </div>`;
    });
}

function acceptLLM(userId){
    const state = llm_state[userId];
    if (!state) return;

    state.accepted = true;

    const outputEl = document.getElementById("llm-output-" + userId);
    outputEl.innerHTML =
    `<div class="card llm-card-overcode">

        <h4>Editar comentário antes de salvar:</h4>

        <textarea id="llm-edit-${userId}" class="textarea-overcode llm-edit-overcode" rows="6">${state.comment}</textarea>

        <button type="button" class="primary action-button-overcode" onclick="saveFinalLLM(${userId})">
            Salvar comentário
        </button>

    </div>`;
}

function rejectLLM(userId){
    const state = llm_state[userId];
    if (!state) return;

    delete llm_state[userId];

    const outputEl = document.getElementById("llm-output-" + userId);

    if(outputEl){
        outputEl.innerHTML = "";
    }
}

function saveFinalLLM(userId){

    const textarea =
        document.getElementById("llm-edit-" + userId);

    const finalComment = textarea.value;

    fetch(window.overcodeConfig.commentUrl, {

        method: "POST",

        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken")
        },

        body: new URLSearchParams({
            user_id: userId,
            selected_user: userId,
            content: finalComment,
            source: "ai"
        })
    })
    .then(async (res) => {

        const data = await res.json();

        if(!res.ok || !data.success){
            throw new Error(data.error || "Erro ao salvar comentário");
        }

        const outputEl =
            document.getElementById("llm-output-" + userId);

        outputEl.innerHTML =`

        <div class="card llm-card-overcode">

            <p>
                Comentário salvo com sucesso.
            </p>

            <div class="divisor-overcode divisor-interno-overcode"></div>

            <h3>
                Avaliação do comentário IA
            </h3>

            ${renderEvaluationForm(userId)}

            <div class="llm-actions-overcode">
                <button type="button" class="primary action-button-overcode" onclick="finishEvaluation(${userId}, ${data.comment_id})">
                    Finalizar formulário
                </button>
            </div>

        </div>
        `;
    })
    .catch(err => {

        const outputEl =
            document.getElementById("llm-output-" + userId);

        outputEl.innerHTML = `
            <div class="card">
                <p>Erro: ${err.message}</p>
            </div>
        `;
    });
}

function renderEvaluationForm(userId){

    return `
    
    ${evaluationQuestion(
        userId,
        "helpful",
        "O comentário foi útil?"
    )}

    ${evaluationQuestion(
        userId,
        "correct",
        "As informações apresentadas estão corretas?"
    )}

    ${evaluationQuestion(
        userId,
        "improve",
        "O comentário ajuda o aluno a melhorar a resposta?"
    )}

    ${evaluationQuestion(
        userId,
        "understand",
        "O comentário ajuda o aluno a entender o conceito?"
    )}

    ${evaluationQuestion(
        userId,
        "contains_code",
        "O comentário possui resposta em código?"
    )}
    
    `;
}

function evaluationQuestion(userId, field, label){

    return `
        
    <div class="evaluation-question-overcode">

        <div class="evaluation-label-overcode">
            <strong>${label}</strong>
        </div>

        <div class="evaluation-options-overcode">
        <label class="evaluation-option-overcode">
            <input
                type="radio"
                name="${field}-${userId}"
                value="true"
            >
            Sim
        </label>

        <label class="evaluation-option-overcode">
            <input
                type="radio"
                name="${field}-${userId}"
                value="false"
            >
            Não
        </label>
        </div>

    </div>
    `;
}

function finishEvaluation(userId, commentId){

    const fields = [
        "helpful",
        "correct",
        "improve",
        "understand",
        "contains_code"
    ];

    let payload = {
        comment_id: commentId,
        user_id: userId
    };

    // validação
    for(let field of fields){

        const checked = document.querySelector(
            `input[name="${field}-${userId}"]:checked`
        );

        if(!checked){

            alert(
                "Preencha todas as perguntas antes de finalizar."
            );

            return;
        }

        payload[field] =
            checked.value === "true";
    }

    fetch(window.overcodeConfig.llmEvaluationUrl, {

        method: "POST",

        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },

        body: JSON.stringify(payload)
    })
    .then(async (res) => {

        const data = await res.json();

        if(!res.ok || !data.success){
            throw new Error(data.error || "Erro ao salvar avaliação");
        }

        window.location.hash = "solution-" + userId;

        location.reload();

    })
    .catch(err => {
        alert(err.message);
    });
}

function getCookie(name){
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener("submit", function(e){
    const form = e.target;

    if(form.tagName !== "FORM") return;

    e.preventDefault();

    const formData = new FormData(form);

    fetch(form.action, {
        method: "POST",
        body: formData,
        headers: {
            "X-CSRFToken": getCookie("csrftoken")
        }
    })
    .then(() => {
        const userId = form.querySelector("input[name='user_id']").value;

        activeUserId = userId;

        setTimeout(() => {
            showSolution(userId);
            window.location.hash = "solution-" + userId;
        }, 0);
    });
});

function reloadSolution(userId){
    fetch(window.location.href, {
        headers: { "X-Requested-With": "fetch" }
    })
    .then(r => r.text())
    .then(html => {
        const parser = new DOMParser()
        const doc = parser.parseFromString(html, "text/html")

        const newSolution = doc.getElementById("solution-" + userId)

        document.getElementById("solution-" + userId).innerHTML =
            newSolution.innerHTML

        hljs.highlightAll()
    })
}
