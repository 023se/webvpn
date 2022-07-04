function changeUrl(oldUrl) {
    // let newUrl = "https://ts1.cn.mm.bing.net/th?id=ORR.6514b15b2e4269248cbade8bb8c643df&pid=Wdp&w=612&h=304&qlt=90&c=1&rs=1&dpr=1&p=0";

    let re = new RegExp(`^${window.location.protocol}//${window.location.host}/https?/`, "g");
    if ( re.test(oldUrl)) {
        // 已经转换过，不用再转换
        return oldUrl;
    }

    if (/^#$/.test(oldUrl)) {
        return oldUrl;
    }
    let newUrl = '';
    re = new RegExp(`^${window.location.protocol}//${window.location.host}`, "g");
    oldUrl=oldUrl.replace(re,`${window.location.pathname.split('/')[0]}://${window.location.pathname.split('/')[1]}`)
    if (/^https:.*/g.test(oldUrl)) {
        // https开头
        let host = oldUrl.split('://', 2)
        newUrl = `${window.location.protocol}//${window.location.host}/https/${host[1]}`
        return newUrl
    }
    else if (/^http:.*/g.test(oldUrl)) {
        // http开头
        let host = oldUrl.split('://', 2)
        newUrl = `${window.location.protocol}//${window.location.host}/http/${host[1]}`
        return newUrl
    }
    else if (/^\w*:/g.test(oldUrl)) {
        // 例如javascript:;
        return oldUrl
    }
    // if (/^\//g.test((oldUrl))) {
    //     // 绝对路径
    //     // /u013288800/article/details/82787641
    //     protrcol=window.location.pathname.split('/')[0];
    //     host=window.location.pathname.split('/')[1];
    //     newUrl = `${window.location.protocol}//${window.location.host}/${protrcol}/${host}${oldUrl}`
    //     return newUrl
    // }

    //其他的都看作是相对路径
    return oldUrl
}

function replace() {
    let tags = document.getElementsByTagName('*');
    for (let i = 0; i < tags.length; i++) {
        let tag = tags[i];
        if (tag.href !== "" && tag.href !== undefined) {
            tag.href = changeUrl(tag.href);
        }
        if (tag.src !== "" && tag.src !== undefined) {
            tag.src = changeUrl(tag.src);
        }
        if (tag.tagName === "FORM" && tag.action !== "" && tag.action !== undefined) {
            tag.action = changeUrl(tag.action);
        }
    }
}

function liner() {
    // 监视网页变化，将元素中的连接转变
    let config = {
        attributes: true, //目标节点的属性变化
        childList: true, //目标节点的子节点的新增和删除
        characterData: true, //如果目标节点为characterData节点(一种抽象接口,具体可以为文本节点,注释节点,以及处理指令节点)时,也要观察该节点的文本内容是否发生变化
        subtree: true, //目标节点所有后代节点的attributes、childList、characterData变化
    };
    let dom = document;
    const mutationCallback = (mutationsList) => {
        for (let mutation of mutationsList) {
            let type = mutation.type;
            switch (type) {
                case "childList":
                    // console.log("A child node has been added or removed.");
                    replace();
                    break;
                case "attributes":
                    // console.log(`The ${mutation.attributeName} attribute was modified.`);
                    break;
                case "subtree":
                    // console.log(`The subtree was modified.`);
                    break;
                default:
                    break;
            }
        }
    };
    let observe = new MutationObserver(mutationCallback);
    observe.observe(dom, config);
}

liner();

