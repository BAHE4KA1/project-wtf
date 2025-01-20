document.addEventListener('DOMContentLoaded', function() {
    const maxMembers = 5;
    const maxLinks = 10;

    function addMember() {
        const dl = document.querySelector('dl');
        const currentMembers = dl.querySelectorAll('dd').length - 1;

        const newButtonId = `button-m-${currentMembers + 1}`;
        const newMemberId = `member-${currentMembers + 1}`;
        const newMember = document.createElement('dd');
        newMember.innerHTML = `<input type="text" id="${newMemberId}" name="member-${currentMembers + 1}" placeholder="Имя Фамилия" required>
                               <button type="button" name="minus" id="${newButtonId}">-</button>`;
        dl.insertBefore(newMember, dl.lastElementChild);

        if (currentMembers === maxMembers - 1) {
            dl.lastElementChild.remove();
        }

        document.getElementById(newButtonId).addEventListener('click', removeMember);
    }

    function removeMember(event) {
        const dl = document.querySelector('dl');
        const member = event.target.parentElement;
        member.remove();

        const members = dl.querySelectorAll('dd input[type="text"]');
        members.forEach((input, index) => {
            input.id = `member-${index + 1}`;
            input.name = `member-${index + 1}`;
            const button = input.nextElementSibling;
            button.id = `button-m-${index + 1}`;
        });

        const currentMembers = members.length;
        if (currentMembers < maxMembers && !dl.querySelector('button[name="plus"]')) {
            const newPlusButton = document.createElement('dd');
            newPlusButton.innerHTML = '<button type="button" name="plus">+</button>';
            dl.appendChild(newPlusButton);
            newPlusButton.querySelector('button[name="plus"]').addEventListener('click', addMember);
        }
    }

    function addLink() {
        const dlLinks = document.querySelector('dl:nth-of-type(2)');
        const currentLinks = dlLinks.querySelectorAll('dd').length - 1;

        const newButtonId = `button-l-${currentLinks + 1}`;
        const newLinkId = `link-${currentLinks + 1}`;
        const newLink = document.createElement('dd');
        newLink.innerHTML = `<input type="text" id="${newLinkId}" name="link-${currentLinks + 1}" placeholder="Ссылка" required>
                             <button type="button" name="minus" id="${newButtonId}">-</button>`;
        dlLinks.insertBefore(newLink, dlLinks.lastElementChild);

        if (currentLinks === maxLinks - 1) {
            dlLinks.lastElementChild.remove();
        }

        document.getElementById(newButtonId).addEventListener('click', removeLink);
    }

    function removeLink(event) {
        const dlLinks = document.querySelector('dl:nth-of-type(2)');
        const link = event.target.parentElement;
        link.remove();

        const links = dlLinks.querySelectorAll('dd input[type="text"]');
        links.forEach((input, index) => {
            input.id = `link-${index + 1}`;
            input.name = `link-${index + 1}`;
            const button = input.nextElementSibling;
            button.id = `button-l-${index + 1}`;
        });

        const currentLinks = links.length;
        if (currentLinks < maxLinks && !dlLinks.querySelector('button[name="plus"]')) {
            const newPlusButton = document.createElement('dd');
            newPlusButton.innerHTML = '<button type="button" name="plus">+</button>';
            dlLinks.appendChild(newPlusButton);
            newPlusButton.querySelector('button[name="plus"]').addEventListener('click', addLink);
        }
    }

    // Привязка событий к кнопкам участников
    document.querySelector('dl button[name="plus"]').addEventListener('click', addMember);
    document.querySelector('dl button[name="minus"]').addEventListener('click', removeMember);

    // Привязка событий к кнопкам ссылок
    document.querySelector('dl:nth-of-type(2) button[name="plus"]').addEventListener('click', addLink);
    document.querySelector('dl:nth-of-type(2) button[name="minus"]').addEventListener('click', removeLink);
});