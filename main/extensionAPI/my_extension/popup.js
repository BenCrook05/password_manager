document.addEventListener('DOMContentLoaded', function () {
    const saveCodeButton = document.getElementById('saveCode');
    const codeInput = document.getElementById('codeInput');

    if (saveCodeButton && codeInput) {
        console.log('checking whether code input required');
        checkCodeRequired()
            .then(code => {
                if (!code) {
                    createCodeInput();
                } else {
                    hideCodeInput();
                }
            })
            .catch(error => {
                console.error('Error checking code requirement:', error);
            });
    }

    saveCodeButton.addEventListener('click', function () {
        const code = codeInput.value;
        if (code.trim() !== '') {
            verifyCode(code)
                .then(verified => {
                    if (!verified) {
                        createCodeInput();
                        console.log("Code invalid");
                    } else {
                        chrome.storage.local.set({ 'storedCode': code }, function () {
                            console.log('Code saved:', code);
                        });
                        console.log("Code valid");
                        hideCodeInput();
                    }
                })
                .catch(error => {
                    console.error('Error verifying code:', error);
                });
        } else {
            console.error('Please enter a code to save.');
        }
    });

    chrome.tabs.onUpdated.addListener(function(tabId, changeInfo, tab) {
        if (changeInfo.url) {
            let temp_url = changeInfo.url;
            console.log('URL changed:', temp_url); 
            let make_request = checkURL(temp_url);

            if (make_request){
                let code = checkCodeRequired()
                if (code != false){
                    let response = callAPI(temp_url,code);
                    console.log(response);
                    if (response['flag'] == "success"){
                        console.log("success");
                        let password = response['password'];
                        let username = response['username'];
                        // display password and username and allow to copy
                        chrome.action.setBadgeText({text: "1"}); // Changes icon to alert passwords has been retrieved
                    } else if (response['flag'] == "error"){
                        console.log("error");
                        if (response['error'] == "Unauthenticated: App refresh required") {
                            console.log("App refresh required");
                            refreshAppAlert()
                        }
                    }
                } else {
                    createCodeInput();
                }

            } else {
                let code = checkCodeRequired();
                if (code == false){
                    createCodeInput();
                } else{
                    hideCodeInput();
                }

            }
        }
        return;
    });
});

function refreshAppAlert(){
    const refreshAppText = document.getElementById('refreshText');
    refreshAppText.style.display = "none";
    return;
}

function hideRefreshAppAlert(){
    const refreshAppText = document.getElementById('refreshText');
    refreshAppText.style.display = "block";
    return;
}


function createCodeInput(){
    const codeInput = document.getElementById('codeInput');
    const saveCodeButton = document.getElementById('saveCode');
    // codeInput.style.display = "none";
    // saveCodeButton.style.display = "none";
    return;
}

function hideCodeInput(){
    const codeInput = document.getElementById('codeInput');
    const saveCodeButton = document.getElementById('saveCode');
    codeInput.style.display = "block";
    saveCodeButton.style.display = "block";
    return;
}



function checkCodeRequired() {
    return new Promise((resolve, reject) => {
        try {
            chrome.storage.local.get('storedCode', function (result) {
                let code = result.storedCode;
                if (code === "codeRequired") {
                    console.log("CodeRequired");
                    resolve(false);
                } else {
                    verifyCode(code)
                        .then(valid => {
                            if (valid) {
                                console.log("CodeValid");
                                resolve(code);
                            } else {
                                resolve(false);
                            }
                        })
                        .catch(error => {
                            reject(error);
                        });
                }
            });
        } catch (error) {
            console.log("CodeRequired");
            console.log(error);
            reject(error);
        }
    });
}



function checkURL(url){
    const common_login_links = ['login','signin','sign-in','signup','sign-up','register','log-in'];
    const common_login_links_length = common_login_links.length;
    for (let i = 0; i < common_login_links_length; i++){
        if (url.includes(common_login_links[i])){
            return true;
        }
    }
    return false;
};

function verifyCode(code){
    const payload = {
        "header": "verify_code",
        "content": {
            "extensioncode": code
        }
    };
    let data = callAPI(payload);
    if (data["code_validity"] == "valid") {
        return true;
    } else {
        return false;
    }
}


function getPassword(url,code){
    const payload = {
        "header": "get_password",
        "content":{
            "extensioncode": code,
            "url": url
        }
    };
    return callAPI(payload);
};

function callAPI(payload){
    fetch('http://127.0.0.1:5000/endpoint', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Response from API:', data);
        return data;
    })
    .catch(error => {
        console.error('Error calling API:, error');
        return {
            "flag": "error",
            "error": error,
            "code_validity": "invalid"
        }
    })
};