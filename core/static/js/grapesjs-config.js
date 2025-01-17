const editor = grapesjs.init({
  // Indicate where to init the editor. You can also pass an HTMLElement
  container: "#gjs",
  // Get the content for the canvas directly from the element
  // As an alternative we could use: `components: '<h1>Hello World Component!</h1>'`,
  fromElement: true,
  plugins: ["grapesjs-tailwind"],
  // Size of the editor
  width: "auto",
  height: "600px",
  // Disable the storage manager for the moment
  mediaCondition: "min-width", // default is `max-width`
  storageManager: {
    type: 'remote',
    stepsBeforeSave: 1,
  },
  deviceManager: {
    devices: [
      {
        name: "Mobile",
        width: "320",
        widthMedia: "",
      },
      {
        name: "Desktop",
        width: "",
        widthMedia: "1024",
      },
    ],
  },
  // Avoid any default panel
  blockManager: {
    appendTo: "#blocks",
    blocks: [
      {
        id: "section", // id is mandatory
        label: "<b>Section</b>", // You can use HTML/SVG inside labels
        attributes: {
          class: "gjs-block-section",
        },
        content: `<section>
<h1>This is a simple title</h1>
<div>This is just a Lorem text: Lorem ipsum dolor sit amet</div>
</section>`,
      },
      {
        id: "text",
        label: "Text",
        content: '<div data-gjs-type="text">Insert your text here</div>',
      },
      {
        id: "image",
        label: "Image",
        // Select the component once it's dropped
        select: true,
        // You can pass components as a JSON instead of a simple HTML string,
        // in this case we also use a defined component type `image`
        content: {
          type: "image",
        },
        // This triggers `active` event on dropped components and the `image`
        // reacts by opening the AssetManager
        activate: true,
      },
    ],
  },
  layerManager: {
    appendTo: ".layers-container",
  },
  // We define a default panel as a sidebar to contain layers
  panels: {
    defaults: [
      {
        id: "layers",
        el: ".panel__right",
        // Make the panel resizable
        resizable: {
          maxDim: 350,
          minDim: 200,
          tc: 0, // Top handler
          cl: 1, // Left handler
          cr: 0, // Right handler
          bc: 0, // Bottom handler
          // Being a flex child we need to change `flex-basis` property
          // instead of the `width` (default)
          keyWidth: "flex-basis",
        },
      },
      {
        id: "panel-devices",
        el: ".panel__devices",
        buttons: [
          {
            id: "device-desktop",
            label: `<i class="fa fa-desktop" aria-hidden="true"></i>`,
            command: "set-device-desktop",
            active: true,
            togglable: false,
          },
          {
            id: "device-mobile",
            label: `<i class="fa fa-mobile" aria-hidden="true"></i>`,
            command: "set-device-mobile",
            togglable: false,
          },
        ],
      },
      {
        id: "panel-switcher",
        el: ".panel__switcher",
        buttons: [
          {
            id: "show-layers",
            active: true,
            label: "Layers",
            command: "show-layers",
            // Once activated disable the possibility to turn it off
            togglable: false,
          },
          {
            id: "show-traits",
            active: true,
            label: "Traits",
            command: "show-traits",
            togglable: false,
          },
          {
            id: "show-style",
            active: true,
            label: "Styles",
            command: "show-styles",
            togglable: false,
          },
          {
            id: "show-blocks",
            active: true,
            label: "Blocos",
            command: "show-blocks",
            togglable: false,
          },
        ],
      },
    ],
  },
  canvas: {
    styles: ["https://cdn.tailwindcss.com"],
    scripts: ["https://cdn.tailwindcss.com"],
  },
  selectorManager: {
    appendTo: ".styles-container",
  },
  styleManager: {
    appendTo: ".styles-container",
    sectors: [
      {
        name: "Dimension",
        open: false,
        // Use built-in properties
        buildProps: ["width", "min-height", "padding"],
        // Use `properties` to define/override single property
        properties: [
          {
            // Type of the input,
            // options: integer | radio | select | color | slider | file | composite | stack
            type: "integer",
            name: "The width", // Label for the property
            property: "width", // CSS property (if buildProps contains it will be extended)
            units: ["px", "%"], // Units, available only for 'integer' types
            defaults: "auto", // Default value
            min: 0, // Min value, available only for 'integer' types
          },
        ],
      },
      {
        name: "Extra",
        open: false,
        buildProps: ["background-color", "box-shadow", "custom-prop"],
        properties: [
          {
            id: "custom-prop",
            name: "Custom Label",
            property: "font-size",
            type: "select",
            defaults: "32px",
            // List of options, available only for 'select' and 'radio'  types
            options: [
              {
                value: "12px",
                name: "Tiny",
              },
              {
                value: "18px",
                name: "Medium",
              },
              {
                value: "32px",
                name: "Big",
              },
            ],
          },
        ],
      },
    ],
  },
  traitManager: {
    appendTo: ".traits-container",
  },
});

editor.setDevice("Mobile");

// Commands
editor.Commands.add("set-device-desktop", {
  run: (editor) => editor.setDevice("Desktop"),
});
editor.Commands.add("set-device-mobile", {
  run: (editor) => editor.setDevice("Mobile"),
});

editor.on("change:device", () =>
  console.log("Current device: ", editor.getDevice())
);

editor.Commands.add("show-traits", {
  getTraitsEl(editor) {
    const row = editor.getContainer().closest(".editor-row");
    return row.querySelector(".traits-container");
  },
  run(editor, sender) {
    this.getTraitsEl(editor).style.display = "";
  },
  stop(editor, sender) {
    this.getTraitsEl(editor).style.display = "none";
  },
});

editor.Commands.add("show-blocks", {
  getTraitsEl(editor) {
    const row = editor.getContainer().closest(".editor-row");
    return row.querySelector("#blocks");
  },
  run(editor, sender) {
    this.getTraitsEl(editor).style.display = "";
  },
  stop(editor, sender) {
    this.getTraitsEl(editor).style.display = "none";
  },
});

// Define commands
editor.Commands.add("show-layers", {
  getRowEl(editor) {
    return editor.getContainer().closest(".editor-row");
  },
  getLayersEl(row) {
    return row.querySelector(".layers-container");
  },

  run(editor, sender) {
    const lmEl = this.getLayersEl(this.getRowEl(editor));
    lmEl.style.display = "";
  },
  stop(editor, sender) {
    const lmEl = this.getLayersEl(this.getRowEl(editor));
    lmEl.style.display = "none";
  },
});
editor.Commands.add("show-styles", {
  getRowEl(editor) {
    return editor.getContainer().closest(".editor-row");
  },
  getStyleEl(row) {
    return row.querySelector(".styles-container");
  },

  run(editor, sender) {
    const smEl = this.getStyleEl(this.getRowEl(editor));
    smEl.style.display = "";
  },
  stop(editor, sender) {
    const smEl = this.getStyleEl(this.getRowEl(editor));
    smEl.style.display = "none";
  },
});

editor.Panels.addPanel({
  id: "panel-top",
  el: ".panel__top",
});
editor.Panels.addPanel({
  id: "basic-actions",
  el: ".panel__basic-actions",
  buttons: [
    {
      id: "visibility",
      active: true, // active by default
      className: "btn-toggle-borders",
      label: "<u>B</u>",
      command: "sw-visibility", // Built-in command
    },
    {
      id: "export",
      className: "btn-open-export",
      label: "Código",
      command: "export-template",
      context: "export-template", // For grouping context of buttons from the same panel
    },
    {
      id: "show-json",
      className: "btn-show-json",
      label: "JSON",
      context: "show-json",
      command(editor) {
        editor.Modal.setTitle("Components JSON")
          .setContent(
            `<textarea style="width:100%; height: 250px; color: black; background-color:white;">
${JSON.stringify(editor.getComponents())}
</textarea>`
          )
          .open();
      },
    },
  ],
});

editor.on("run:export-template:before", (opts) => {
  console.log("Before the command run");
  if (0 /* some condition */) {
    opts.abort = 1;
  }
});
editor.on("run:export-template", () => console.log("After the command run"));
editor.on("abort:export-template", () => console.log("Command aborted"));
