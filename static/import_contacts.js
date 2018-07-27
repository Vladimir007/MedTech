$(document).on('change', '.btn-file :file', function () {
    let input = $(this),
        numFiles = input.get(0).files ? input.get(0).files.length : 1,
        label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
    input.trigger('fileselect', [numFiles, label]);
});

$(document).ready(function () {
    $('#import_fileinput').on('fileselect', function () {
        let files = $(this)[0].files, filename_container = $('#import_filename');
        files.length ? filename_container.text(files[0].name) : filename_container.empty();
    });
});
