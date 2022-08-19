{
  description = "Bot for keeping order in your Telegram chat";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix.url = "github:nix-community/poetry2nix";
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    {
      overlays.default = nixpkgs.lib.composeManyExtensions [
        poetry2nix.overlay
        (final: prev: {
          ugragatekeeper = final.poetry2nix.mkPoetryApplication {
            python = final.python310;

            projectDir = ./.;

            postInstall = ''
              install -Dm644 config-clean.yaml $out/etc/ugragatekeeper.yaml
            '';
          };
        })
      ];

      nixosModules.ugragatekeeper.imports = [
        ({ pkgs, ... }: {
          nixpkgs.overlays = [ self.overlays.default ];
        })
        (import ./module.nix)
      ];
    } // (flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ self.overlays.default ];
        };

        app = flake-utils.lib.mkApp {
          drv = pkgs.ugragatekeeper;
        };
      in
      {
        packages = {
          ugragatekeeper = pkgs.ugragatekeeper;
          default = pkgs.ugragatekeeper;
        };

        apps = {
          ugragatekeeper = app;
          default = app;
        };
      }));
}
