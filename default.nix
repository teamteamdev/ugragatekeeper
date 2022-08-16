{ pkgs ? import <nixpkgs> {} }:

pkgs.poetry2nix.mkPoetryApplication {
  projectDir = ./.;

  postInstall = ''
    mkdir -p $out/etc
    cp $src/config-example.yaml $out/etc/moderator.yaml
  '';
}
