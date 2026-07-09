
/* JS */

let studentsPerPage = 8
let currentPage = 1

let students = []
let filtered = []
let solutions = []

let currentSolutionIndex = null

let llm_state = {}

function solutionHash(id){
    return "#solution-" + id
}

function updateUrlHash(hash){
    if(window.location.hash === hash){
        return
    }

    window.history.replaceState(
        null,
        "",
        window.location.pathname + window.location.search + hash
    )
}

function clearSolutionHash(){
    if(!window.location.hash.match(/^#solution-\d+$/)){
        return
    }

    window.history.replaceState(
        null,
        "",
        window.location.pathname + window.location.search
    )
}

function clearSelectedSolutionState(){
    currentSolutionIndex = null

    sessionStorage.removeItem(
        "active_solution"
    )

    clearSolutionHash()
}

function setRepresentativeState(){
    sessionStorage.setItem(
        "active_group",
        window.overcodeConfig?.groupId || ""
    )

    sessionStorage.setItem(
        "active_tab",
        "representative"
    )

    clearSelectedSolutionState()
}

function setSolutionsListState(){
    sessionStorage.setItem(
        "active_group",
        window.overcodeConfig?.groupId || ""
    )

    sessionStorage.setItem(
        "active_tab",
        "solutions"
    )

    clearSelectedSolutionState()
}

function setSolutionState(id){
    sessionStorage.setItem(
        "active_group",
        window.overcodeConfig?.groupId || ""
    )

    sessionStorage.setItem(
        "active_tab",
        "solutions"
    )

    sessionStorage.setItem(
        "active_solution",
        id
    )

    updateUrlHash(solutionHash(id))
}

function escapeHtml(text){
    return (text || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
}

function normalizeMarkdown(text){
    return (text || "")
        .replace(/\r\n/g, "\n")
        .replace(/^[ \t]+(#{1,6}\s+)/gm, "$1")
        .replace(/^[ \t]+([-*]\s+)/gm, "$1")
}

function fallbackMarkdownToHtml(text){
    const lines = normalizeMarkdown(text).split("\n")
    let html = ""
    let inList = false

    lines.forEach(function(line){
        const trimmed = line.trim()

        if(!trimmed){
            if(inList){
                html += "</ul>"
                inList = false
            }
            return
        }

        const heading = trimmed.match(/^(#{1,6})\s+(.+)$/)
        if(heading){
            if(inList){
                html += "</ul>"
                inList = false
            }

            const level = Math.min(heading[1].length, 6)
            html += `<h${level}>${escapeHtml(heading[2])}</h${level}>`
            return
        }

        const bullet = trimmed.match(/^[-*]\s+(.+)$/)
        if(bullet){
            if(!inList){
                html += "<ul>"
                inList = true
            }

            html += `<li>${escapeHtml(bullet[1])}</li>`
            return
        }

        if(inList){
            html += "</ul>"
            inList = false
        }

        html += `<p>${escapeHtml(trimmed)}</p>`
    })

    if(inList){
        html += "</ul>"
    }

    return html
}

function markdownToHtml(text){
    const markdown = normalizeMarkdown(text)

    if (window.showdown) {
        const converter = new showdown.Converter({
            simplifiedAutoLink: true,
            simpleLineBreaks: true
        })

        return converter.makeHtml(escapeHtml(markdown))
    }

    return fallbackMarkdownToHtml(markdown)
}

function saveCurrentView(){
    sessionStorage.setItem(
        "active_group",
        window.overcodeConfig?.groupId || ""
    )

    const solutionsTab =
        document.getElementById("solutions")

    const isSolutionsVisible =
        solutionsTab.style.display !== "none"

    if(isSolutionsVisible){

        if(currentSolutionIndex !== null){

            const currentId =
                solutions[currentSolutionIndex]
                ?.id
                ?.replace("solution-", "")

            if(currentId){
                setSolutionState(currentId)
                return
            }
        }

        setSolutionsListState()
        return
    }else{

        setRepresentativeState()
    }
}

function init(){
students = [...document.querySelectorAll(".student")]
solutions = [...document.querySelectorAll(".solution-detail")]
filtered = [...students]
renderSavedComments()
showPage(1)
}

function renderSavedComments(){
    document
        .querySelectorAll(".comment-text-overcode")
        .forEach(function(comment){
            const markdown = comment.textContent
            comment.innerHTML = markdownToHtml(markdown)
            comment.classList.add("llm-markdown-overcode")
        })
}

function hideAll(elements){
elements.forEach(e => e.style.display="none")
}

function showPage(page){
currentPage = page
hideAll(students)

let start = (page-1) * studentsPerPage
let end = start + studentsPerPage

filtered.slice(start,end).forEach(el=>{
el.style.display="block"
})

let total = Math.ceil(filtered.length/studentsPerPage)

document.getElementById("page-info").innerText =
page+" / "+total
}

function nextPage(){
let total=Math.ceil(filtered.length/studentsPerPage)
if(currentPage<total) showPage(currentPage+1)
}

function prevPage(){
if(currentPage>1) showPage(currentPage-1)
}

function searchStudent(){
let value=document.getElementById("search").value.toLowerCase()
filtered = students.filter(el =>
el.dataset.name.includes(value)
)
showPage(1)
}

function showSolution(id){

    document.getElementById(
        "student-section"
    ).style.display = "none"

    hideAll(solutions)

    let element =
        document.getElementById(
            "solution-" + id
        )

    if(element){
        element.style.display = "block"
    }

    currentSolutionIndex =
        solutions.findIndex(
            el => el.id === "solution-" + id
        )

    setSolutionState(id)
}

function nextSolution(){
if(currentSolutionIndex < solutions.length-1){
solutions[currentSolutionIndex].style.display="none"
currentSolutionIndex++
solutions[currentSolutionIndex].style.display="block"
}
}

function prevSolution(){
if(currentSolutionIndex>0){
solutions[currentSolutionIndex].style.display="none"
currentSolutionIndex--
solutions[currentSolutionIndex].style.display="block"
}
}

function backToStudents(){

    setSolutionsListState()

    hideAll(solutions)

    document.getElementById(
        "student-section"
    ).style.display = "block"
}

function openTab(tab){

    document
        .querySelectorAll("[data-tab-target]")
        .forEach(function(button){
            button.classList.toggle(
                "active-overcode",
                button.dataset.tabTarget === tab
            )
        })

    document.getElementById(
        "representative"
    ).style.display = "none"

    document.getElementById(
        "solutions"
    ).style.display = "none"

    document.getElementById(tab)
        .style.display = "block"

    if(tab === "solutions"){
        setSolutionsListState()

        document.getElementById(
            "student-section"
        ).style.display = "block"

        hideAll(solutions)
    }else{
        setRepresentativeState()
    }
}

window.onload = function(){

    init()

    sessionStorage.removeItem("active_tab")
    sessionStorage.removeItem("active_solution")

    const selectedSolution =
        window.location.hash.match(/^#solution-(\d+)$/)

    if(selectedSolution){
        openTab("solutions")
        showSolution(selectedSolution[1])
        return
    }

    openTab("representative")
}

function generateLLMGroupComment(groupId){

    setRepresentativeState()

    const loadingEl = document.getElementById("llm-loading-" + groupId)
    const outputEl = document.getElementById("llm-output-" + groupId)

    if (loadingEl) loadingEl.style.display = "block"
    if (outputEl) outputEl.innerHTML = ""

    const code =
        document.querySelector("#representative .code-block-overcode pre")
        ?.innerText || ""

    fetch(window.overcodeConfig.llmGroupCommentUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({
            code: code,
            group_id: groupId
        })
    })
    .then(async (res) => {

        const text = await res.text()

        let data

        try{
            data = JSON.parse(text)
        }catch(e){
            throw new Error("Resposta inválida do servidor")
        }

        if(!res.ok){
            throw new Error(data.error || "Erro na API")
        }

        return data
    })
    .then(data => {

        if (loadingEl)
            loadingEl.style.display = "none"

        const comment =
            data?.comment || "Sem resposta da IA"

        llm_state[groupId] = {
            comment: comment
        }

        const commentHtml = markdownToHtml(comment)

        outputEl.innerHTML = `
            <div class="card llm-card-overcode">

                <p>
                    <strong>
                        Comentário sugerido pela IA:
                    </strong>
                </p>

                <div class="llm-markdown-overcode">${commentHtml}</div>

                <div class="llm-actions-overcode">
                    <button type="button" class="primary action-button-overcode" onclick="acceptLLM(${groupId}, true)">
                        Usar comentário
                    </button>

                    <button type="button" class="secondary-button-overcode" onclick="rejectLLM(${groupId})">
                        Não usar
                    </button>
                </div>

            </div>
        `
    })
    .catch(err => {

        if (loadingEl)
            loadingEl.style.display = "none"

        outputEl.innerHTML = `
            <div class="card">
                <p>Erro: ${err.message}</p>
            </div>
        `
    })
}

function generateLLMForStudent(userId){

    setSolutionState(userId)

    const loadingEl = document.getElementById("llm-loading-" + userId)
    const outputEl = document.getElementById("llm-output-" + userId)

    if (loadingEl) loadingEl.style.display = "block"
    if (outputEl) outputEl.innerHTML = ""

    const solutionEl = document.getElementById("solution-" + userId)

    const code = solutionEl
        ? solutionEl.querySelector(".code-block-overcode pre")?.innerText || ""
        : ""

    fetch(window.overcodeConfig.llmGroupCommentUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify({
            code: code,
            group_id: null,
            user_id: userId
        })
    })
    .then(async (res) => {

        const text = await res.text()

        let data
        try {
            data = JSON.parse(text)
        } catch (e) {
            throw new Error("Resposta inválida do servidor: " + text)
        }

        if (!res.ok) {
            throw new Error(data.error || "Erro na API")
        }

        return data
    })
    .then(data => {

        if (loadingEl)
            loadingEl.style.display = "none"

        const comment =
            data?.comment || "Sem resposta da IA"

        llm_state[userId] = {
            comment: comment
        }

        const commentHtml = markdownToHtml(comment)

        outputEl.innerHTML = `
            <div class="card llm-card-overcode">

                <p>
                    <strong>
                        Comentário sugerido pela IA:
                    </strong>
                </p>

                <div class="llm-markdown-overcode">${commentHtml}</div>

                <div class="llm-actions-overcode">
                    <button type="button" class="primary action-button-overcode" onclick="acceptLLM(${userId}, false)">
                        Usar comentário
                    </button>

                    <button type="button" class="secondary-button-overcode" onclick="rejectLLM(${userId})">
                        Não usar
                    </button>
                </div>

            </div>
        `
    })
    .catch(err => {

        if (loadingEl) loadingEl.style.display = "none"

        outputEl.innerHTML = `
            <div class="card">
                <p>Erro: ${err.message}</p>
            </div>
        `
    })
}

function sendFeedback(groupId, value){
console.log("feedback:", groupId, value)
// depois conectamos no banco
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

function acceptLLM(id, isGroup){

    if(isGroup){
        setRepresentativeState()
    }else{
        setSolutionState(id)
    }

    const state = llm_state[id]

    if(!state) return

    const outputEl =
        document.getElementById("llm-output-" + id)

    outputEl.innerHTML = `

        <div class="card llm-card-overcode">

            <h4>
                Editar comentário antes de salvar:
            </h4>

            <textarea id="llm-edit-${id}" class="textarea-overcode llm-edit-overcode" rows="6">${state.comment}</textarea>

            <button type="button" class="primary action-button-overcode" onclick="saveFinalLLM(${id}, ${isGroup})">
                Salvar comentário
            </button>

        </div>
    `
}

function rejectLLM(id){

    const outputEl =
        document.getElementById("llm-output-" + id)

    delete llm_state[id]

    if(outputEl){
        outputEl.innerHTML = ""
    }
}

function saveFinalLLM(id, isGroup){

    if(isGroup){
        setRepresentativeState()
    }else{
        setSolutionState(id)
    }

    const textarea =
        document.getElementById("llm-edit-" + id)

    const finalComment = textarea.value

    let bodyData = {
        content: finalComment,
        source: "ai"
    }

    if(isGroup){
        bodyData.group_id = id
    }else{
        bodyData.user_id = id
        bodyData.selected_user = id
        bodyData.group_id = window.overcodeConfig.groupId
    }

    fetch(window.overcodeConfig.commentUrl, {

        method: "POST",

        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken")
        },

        body: new URLSearchParams(bodyData)
    })
    .then(async (res) => {

        const data = await res.json()

        if(!res.ok || !data.success){
            throw new Error(data.error || "Erro ao salvar comentário")
        }

        const outputEl =
            document.getElementById("llm-output-" + id)

        outputEl.innerHTML = `

            <div class="card llm-card-overcode">

                <p>
                    Comentário salvo com sucesso.
                </p>

                <div class="divisor-overcode divisor-interno-overcode"></div>

                <h3>
                    Avaliação do comentário IA
                </h3>

                ${renderEvaluationForm(id)}

                <div class="llm-actions-overcode">
                    <button type="button" class="primary action-button-overcode" onclick="finishEvaluation(${id}, ${isGroup}, ${data.comment_id}, this)">
                        Finalizar formulário
                    </button>
                </div>

            </div>
        `
    })
    .catch(err => {

        const outputEl =
            document.getElementById("llm-output-" + id)

        outputEl.innerHTML = `
            <div class="card">
                <p>Erro: ${err.message}</p>
            </div>
        `
    })
}

function renderEvaluationForm(id){

    return `

    ${evaluationQuestion(
        id,
        "helpful",
        "O comentário foi útil?"
    )}

    ${evaluationQuestion(
        id,
        "correct",
        "As informações apresentadas estão corretas?"
    )}

    ${evaluationQuestion(
        id,
        "improve",
        "O comentário ajuda o aluno a melhorar a resposta?"
    )}

    ${evaluationQuestion(
        id,
        "understand",
        "O comentário ajuda o aluno a entender o conceito?"
    )}

    ${evaluationQuestion(
        id,
        "contains_code",
        "O comentário possui resposta em código?"
    )}
    `
}

function evaluationQuestion(id, field, label){

    return `

    <div class="evaluation-question-overcode">

        <div class="evaluation-label-overcode">
            <strong>${label}</strong>
        </div>

        <div class="evaluation-options-overcode">
        <label class="evaluation-option-overcode">
            <input
                type="radio"
                name="${field}-${id}"
                value="true"
            >
            Sim
        </label>

        <label class="evaluation-option-overcode">
            <input
                type="radio"
                name="${field}-${id}"
                value="false"
            >
            Não
        </label>
        </div>

    </div>
    `
}

function finishEvaluation(id, isGroup = false, commentId = null, button = null){

    const fields = [
        "helpful",
        "correct",
        "improve",
        "understand",
        "contains_code"
    ]

    let payload = {
        comment_id: commentId
    }

    if(isGroup){
        payload.group_id = id
    }else{
        payload.user_id = id
    }

    for(let field of fields){

        const checked = document.querySelector(
            `input[name="${field}-${id}"]:checked`
        )

        if(!checked){

            alert(
                "Preencha todas as perguntas antes de finalizar."
            )

            return
        }

        payload[field] =
            checked.value === "true"
    }

    if(button){
        button.disabled = true
        button.dataset.originalText = button.textContent
        button.textContent = "Salvando avaliação..."
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

        const data = await res.json()

        if(!res.ok || !data.success){
            throw new Error(data.error || "Erro ao salvar avaliação")
        }

        if(!isGroup){
            setSolutionState(id)

            window.location.hash = solutionHash(id)
            location.reload()

            return
        }

        setRepresentativeState()
        location.reload()
    })
    .catch(err => {
        if(button){
            button.disabled = false
            button.textContent =
                button.dataset.originalText || "Finalizar formulário"
        }

        alert(err.message)
    })
}
